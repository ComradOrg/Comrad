"""
There is only one operator!
Running on node prime.
"""
import os
from flask import Flask
from flask import request
import asyncio
from pythemis.skeygen import KEY_PAIR_TYPE, GenerateKeyPair
from pythemis.smessage import SMessage, ssign, sverify
from pythemis.exception import ThemisError
from base64 import b64encode,b64decode
BSEP=b'||||||||||'
BSEP2=b'@@@@@@@@@@'
BSEP3=b'##########'

HOME_OPERATOR = os.path.abspath(__file__)
PATH_DB_KEYS = os.path.join(HOME_OPERATOR, '.keydb')

keyhome = os.path.join(os.path.expanduser('~'),'.komrade','.keyserver')
if not os.path.exists(keyhome): os.makedirs(keyhome)

keyserver = 'komrade.app'
keyserver_port = 5566

app = Flask(__name__)

async def init():
    from api import Api
    api = Api()
    # keyserver = await api.personate('keyserver')

    keypair = GenerateKeyPair(KEY_PAIR_TYPE.EC)
    privkey = keypair.export_private_key()
    pubkey = keypair.export_public_key()

    print('pubkey:',pubkey)
    with open('.keyserver.loc','wb') as of: of.write(b64encode(pubkey))
    with open(os.path.join(keyhome,'.keyserver.key'),'wb') as of: of.write(b64encode(privkey))    

## load pubkey
PATH_PUBKEY = os.path.join(os.path.dirname(__file__),'.keyserver.loc')
PATH_PRIVKEY = os.path.join(keyhome,'.keyserver.key')
if not os.path.exists(PATH_PRIVKEY) or not os.path.exists(PATH_PUBKEY):
    asyncio.run(init())

with open(PATH_PUBKEY) as f:
    PUBKEY_b64 = f.read()
    PUBKEY = b64decode(PUBKEY_b64)
with open(PATH_PRIVKEY) as f:
    PRIVKEY_b64 = f.read()
    PRIVKEY = b64decode(PRIVKEY_b64)

@app.route('/pub')
def pubkey():
    return PUBKEY_b64

@app.route('/add/<name>',methods=['POST'])
def add(name):
    key_fn = os.path.join(keyhome,name+'.loc')
    if not os.path.exists(key_fn):
        with open(key_fn,'wb') as of:
            pubkey,signed_pubkey=request.data.split(BSEP)
            server_signed_pubkey = b64encode(ssign(PRIVKEY,pubkey))
            package = pubkey + BSEP + signed_pubkey + BSEP + server_signed_pubkey
            package_b64 = b64encode(package)
            print('add package -->',package)     
            print('add package_b64 -->',package_b64)
            of.write(package_b64)
            return package_b64
    return None

@app.route('/get/<name>')
def get(name):
    key_fn = os.path.join(keyhome,name+'.loc')
    if os.path.exists(key_fn):
        with open(key_fn,'rb') as f:
            signed_key=f.read()
            return signed_key
    return b''

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=keyserver_port)
    # asyncio.run(init())