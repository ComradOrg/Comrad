"""
There is only one operator!
Running on node prime.
"""
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade.backend.crypt import Crypt
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




class Operator(Keymaker):
    ### INIT CODE
    def __init__(self,name):
        self.name=name
        # self.op = TheOperator()

    ## CRYPT BASICS
    
class Caller(Operator):
    @property
    def crypt_cell(self):
        pass




class TheOperator(Operator):
    """
    The operator.
    """

    def __init__(self, name = 'TheOperator'):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """
        self.name = name

        # Do I have my keys?
        have_keys = self.have_keys()

        # If not, forge them -- only once!
        if not have_keys: self.forge_keys()

        # load keys
        # self.pubkey,self.privkey = self.get_op_keys()
        
        # That's it!

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