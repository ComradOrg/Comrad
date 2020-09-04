"""
There is only one operator!
Running on node prime.
"""
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade.backend.crypt import Crypt
from komrade.backend.caller import Caller
from komrade.backend.keymaker import Keymaker
from flask import Flask
from flask_classful import FlaskView
from pythemis.skeygen import KEY_PAIR_TYPE, GenerateKeyPair
from pythemis.smessage import SMessage, ssign, sverify
from pythemis.skeygen import GenerateSymmetricKey
from pythemis.scell import SCellSeal
from pythemis.exception import ThemisError
from base64 import b64encode,b64decode
from komrade import KomradeException,Logger
import getpass
PATH_HERE = os.path.dirname(__file__)
sys.path.append(PATH_HERE)
from crypt import *
### Constants
BSEP=b'||||||||||'
BSEP2=b'@@@@@@@@@@'
BSEP3=b'##########'


# paths
PATH_KOMRADE = os.path.abspath(os.path.join(os.path.expanduser('~'),'.komrade'))
PATH_OPERATOR = os.path.join(PATH_KOMRADE,'.operator')
PATH_OPERATOR_PUBKEY = os.path.join(PATH_OPERATOR,'.op.key.pub.encr')
PATH_OPERATOR_PRIVKEY = os.path.join(PATH_OPERATOR,'.op.key.priv.encr')
PATH_CRYPT_KEYS = os.path.join(PATH_OPERATOR,'.op.db.keys.crypt')
PATH_CRYPT_DATA = os.path.join(PATH_OPERATOR,'.op.db.data.encr')

# init req paths
if not os.path.exists(PATH_OPERATOR): os.makedirs(PATH_OPERATOR)




class TheOperator(Caller):
    """
    The operator.
    """
    PATH_CRYPT_KEYS=PATH_CRYPT_KEYS
    PATH_CRYPT_DATA=PATH_CRYPT_DATA


    def __init__(self, name = 'Operator', passphrase = None):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """
        self.name = name

        # Do I have my keys?
        have_keys = self.have_keys()

        # If not, forge them -- only once!
        # if not have_keys: self.forge_keys()

        # load keys
        # self.pubkey,self.privkey = self.get_op_keys()
        
        # That's it!

    def have_keys(self):
        self.log('checking for keys...')
        have_keys = self.crypt_keys.get(self.name,prefix='/pubkey_encr/')
        self.log('have_keys =',have_keys)
        return have_keys

    # def forge_keys(self):
    #     self.log('forging keys...')

    #     # first time only!
    #     # this will save the three encrypted keys
    #     # all are returned, including the decryptor keys
    #     keychain = self.create_keys(self.name,return_all_keys=True)
        
        
        
    
    ####
    # Key CRUD
    ####

    def forge_new_keys(self,name,pubkey_is_public=False,return_all_keys=False):
        self.log('forging new keys...')

        # Create public and private keys
        keypair = GenerateKeyPair(KEY_PAIR_TYPE.EC)
        privkey = keypair.export_private_key()
        pubkey = keypair.export_public_key()
        adminkey = GenerateSymmetricKey()

        # Create decryption/permission keys
        pubkey_decr = GenerateSymmetricKey()
        privkey_decr = GenerateSymmetricKey()
        adminkey_decr = GenerateSymmetricKey() #SCellSeal(passphrase=passphrase)
        
        # Encrypt original keys
        pubkey_encr = SCellSeal(key=pubkey_decr).encrypt(pubkey)
        privkey_encr = SCellSeal(key=privkey_decr).encrypt(privkey)
        adminkey_encr = SCellSeal(key=adminkey_decr).encrypt(adminkey)

        # store encrypted on my hardware
        self.crypt_keys.set(name,pubkey_encr,prefix='/pubkey_encr/')
        self.crypt_keys.set(pubkey,privkey_encr,prefix='/privkey_encr/')
        self.crypt_keys.set(privkey,adminkey_encr,prefix='/adminkey_encr/')

        # store permissions file?
        secret_admin_val = pubkey_encr + BSEP + b'find,read,admin'
        if pubkey_is_public: secret_admin_val += b'*'+BSEP+b'find'
        secret_admin_val_encr = SCellSeal(key=adminkey).encrypt(secret_admin_val)
        self.crypt_keys.set(adminkey,secret_admin_val_encr,prefix='/permkey_encr/')

        # keep public key?
        if pubkey_is_public: self.crypt_keys.set(name,pubkey_decr,prefix='/pubkey_decr/')
        
        # send back decryption keys to client
        if not return_all_keys: # default situation
            keychain = {
                'pubkey_decr':pubkey_decr,
                'privkey_decr':privkey_decr,
                'adminkey_decr':adminkey_decr
            }
        else: # only in special case!
            keychain = {
                'pubkey':pubkey,'pubkey_encr':pubkey_encr,'pubkey_decr':pubkey_decr,
                'privkey':privkey,'privkey_encr':privkey_encr,'privkey_decr':privkey_decr,
                'adminkey':adminkey,'adminkey_encr':adminkey_encr,'adminkey_decr':adminkey_decr
            }
        return keychain
        
        

    # Magic key attributes


    ## DECRYPTED REAL FINAL KEYS

    def pubkey(self, name, keychain_decr):
        pubkey_decr = keychain_decr.get('pubkey_decr')
        pubkey_encr = self.pubkey_encr(name)
        if not pubkey_decr or not pubkey_encr: return None
        pubkey = SCellSeal(key=pubkey_decr).decrypt(pubkey_encr)
        return pubkey


    def privkey(self, name, keychain_decr):
        privkey_decr = keychain_decr.get('privkey_decr')
        privkey_encr = self.privkey_encr(name, keychain_decr)
        if not privkey_decr or not privkey_encr: return None
        privkey = SCellSeal(key=privkey_decr).decrypt(privkey_encr)
        return privkey

    def adminkey(self, name, keychain_decr):
        adminkey_decr = keychain_decr.get('adminkey_decr')
        adminkey_encr = self.adminkey_encr(name, keychain_decr)
        if not adminkey_decr or not adminkey_encr: return None
        adminkey = SCellSeal(key=adminkey_decr).decrypt(adminkey_encr)
        return adminkey



    def exists(self,name):
        return self.crypt_keys.get(name,prefix='/pubkey_encr/') is not None

    def login(self, name, keychain_encr):
        pass










class TheOperatorView(FlaskView):
    route_prefix = '/'
    def index(self):
        print('hello')
        return "<br>".join(quotes)

    def something(self):
        return 'something'






def get_random_id():
    import uuid
    return uuid.uuid4().hex

def get_random_binary_id():
    import base64
    idstr = get_random_id()
    return base64.b64encode(idstr.encode())






## Main

def run_forever():
    app = Flask(__name__)
    TheOperator.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=True)

if __name__ == '__main__':
    #run_forever()

    op = TheOperator()
    
    #print(op.crypt_keys.set('aaaa','1111'))

    # print(op.crypt_keys.get('aaaa'))
    # print(op.forge_keys())