"""
There is only one operator!
Running on node prime.
"""
import os,sys
from flask import Flask
from flask_classful import FlaskView
from pythemis.skeygen import KEY_PAIR_TYPE, GenerateKeyPair
from pythemis.smessage import SMessage, ssign, sverify
from pythemis.skeygen import GenerateSymmetricKey
from pythemis.scell import SCellSeal
from pythemis.exception import ThemisError
from base64 import b64encode,b64decode
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




class TheOperator(object):
    """
    The operator.
    """


    def __init__(self):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """

        # Establish encryption/decryption cell
        self.cell = SCellSeal(passphrase=getpass.getpass('What is the password of memory? '))

        # Do I have my keys?
        have_keys = self.check_keys()

        # If not, forge them -- only once!
        if not have_keys: self.forge_keys()

        # load keys
        self.pubkey,self.privkey = self.get_keys()
        
        # That's it!
        

    @property
    def crypt_keys(self):
        if not hasattr(self,'_crypt_keys'):
            self._crypt_keys = Crypt(fn=PATH_CRYPT_KEYS, cell=self.cell)
        return self._crypt_keys

    @property
    def crypt_data(self):
        if not hasattr(self,'_crypt_data'):
            self._crypt_data = Crypt(fn=PATH_CRYPT_DATA, cell=self.cell)
        return self._crypt_data

    def log(self,*x):
        print(*x)

    def get_encypted_keys(self):
        self.log('loading encrypted keys from disk')
        with open(PATH_OPERATOR_PUBKEY,'rb') as f_pub, open(PATH_OPERATOR_PRIVKEY,'rb') as f_priv:
            pubkey_encr = f_pub.read()
            privkey_encr = f_priv.read()
            #self.log('loaded encrypted pubkey is:',pubkey_encr)
            #self.log('loaded encrypted privkey is:',privkey_encr)
            return (pubkey_encr,privkey_encr)

    def get_keys(self):
        pubkey_encr,privkey_encr = self.get_encypted_keys()

        # decrypt according to password of memory
        try:
            pubkey = self.cell.decrypt(pubkey_encr)
            privkey = self.cell.decrypt(privkey_encr)
        except ThemisError:
            self.log('\nERROR: Incorrect password of memory! Shutting down.')
            exit()

        # self.log(f'decrypted keys to:\npubkey={pubkey}\nprivkey={privkey}')
        return (pubkey,privkey)
        

    def check_keys(self):
        self.log('checking for keys...')
        have_keys = (os.path.exists(PATH_OPERATOR_PUBKEY) and os.path.exists(PATH_OPERATOR_PRIVKEY))
        self.log('have_keys =',have_keys)
        return have_keys

    def forge_keys(self):
        self.log('forging keys...')

        # Initialize asymmetric keys
        keypair = GenerateKeyPair(KEY_PAIR_TYPE.EC)
        privkey = keypair.export_private_key()
        pubkey = keypair.export_public_key()

        # Also create a symmetric passworded key!
        ## It is up to you, forger of the keys, to remember this:
        ## otherwise the whole system topples!
        
        # Encrypt private public keys
        privkey = self.cell.encrypt(privkey)
        pubkey = self.cell.encrypt(pubkey)

        # Save
        with open(PATH_OPERATOR_PUBKEY,'wb') as of: of.write(pubkey)
        with open(PATH_OPERATOR_PRIVKEY,'wb') as of: of.write(privkey)

        self.log('Keys forged!')


    
    ####
    # Key CRUD
    ####

    def create_keys(self,name,pubkey_is_public=False):

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
        self.crypt_keys.set(name,pubkey_encr,prefix='/pub_encr/')
        self.crypt_keys.set(pubkey,privkey_encr,prefix='/priv_encr/')
        self.crypt_keys.set(privkey,adminkey_encr,prefix='/admin_encr/')

        # store permissions file?
        secret_admin_val = pubkey_encr + BSEP + b'find,read,admin'
        if pubkey_is_public: secret_admin_val += b'*'+BSEP+b'find'
        secret_admin_val_encr = SCellSeal(key=adminkey).encrypt(secret_admin_val)
        self.crypt_keys.set(adminkey,secret_admin_val_encr,prefix='/perm_encr/')

        # keep public key?
        if pubkey_is_public: self.crypt_keys.set(name,pubkey_decr,prefix='/pub_decr/')
        
        # send back decryption keys to client
        return (pubkey_decr, privkey_decr, adminkey_decr)
        


    def exists(self,name):
        return self.crypt_keys.get(name,prefix='/pub_encr/') is not None












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
    op.create_keys(name='marx')