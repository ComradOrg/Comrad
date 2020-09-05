"""
There is only one operator!
Running on node prime.
"""
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade.operators.crypt import Crypt
from komrade.operators.keymaker import Keymaker
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
    
    def __init__(self, name, passphrase=None):
        super().__init__(name=name,passphrase=passphrase)

    def boot(self,create=False):
         # Do I have my keys?
        have_keys = self.exists()
        
        # If not, forge them -- only once!
        if not have_keys and create:
            self.get_new_keys()

        # load keychain into memory
        self._keychain = self.keychain(force = True)


class Caller(Operator):
    def get_new_keys(self,pubkey_pass = None, privkey_pass = None, adminkey_pass = None):
        # Get decryptor keys back from The Operator (one half of the Keymaker)
        keychain = self.forge_new_keys(self.name)
        self.log('create_keys() res from Operator? <-',keychain)

        # Now lock the decryptor keys away, sealing it with a password of memory!
        self.lock_new_keys(keychain)

class TheOperator(Operator):
    """
    The remote operator! Only one!
    """

    def __init__(self, name = 'TheOperator', passphrase=None):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """
        if not passphrase:
            passphrase=getpass.getpass('Hello, this is the Operator speaking. What is the passphrase?\n> ')
        super().__init__(name,passphrase)



OPERATOR = None
class TheOperatorsSwitchboard(FlaskView):
    def index(self):
        return OPERATOR.keychain()['pubkey']
        
    def something(self):
        return 'something'


def run_forever():
    global OPERATOR
    OPERATOR = TheOperator()
    app = Flask(__name__)
    TheOperatorsSwitchboard.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=True)

if __name__ == '__main__':
    run_forever()
