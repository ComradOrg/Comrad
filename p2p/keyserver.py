"""
Run primitive keyserver
Only on node prime!
"""
import os
from flask import Flask

keyhome = os.path.join(os.path.expanduser('~'),'.komrade','.keyserver')
# if not os.path.exists(keyhome): os.makedirs(keyhome)

keyserver = 'komrade.app'
keyserver_port = 5566

app = Flask(__name__)

async def init():
    if not os.path.exists(keyhome):
        from api import Api()
        keyserver = await api.personate('keyserver')
    


@app.route('/')
def hello():
    return "Hello World!"

@app.route('/add/<name>/<key>')
def add(name,key):
    key_fn = os.path.join(key_path,name+'.loc')
    if os.path.exists(key_fn):
        with open(key_fn,'wb') as of:
            of.write(key)
            return key
    return None
    
if __name__ == '__main__':
    # app.run(host='0.0.0.0',port=keyserver_port)
    asyncio.run(init())