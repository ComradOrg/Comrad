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

        #self.boot(create=True)



    # # ca = RemoteOperator(name='elon')
    # # # ca.get_new_keys()
    # # op.boot()
    # # ca.boot()
    
    # #print(op.crypt_keys.set('aaaa','1111'))

    # # print(op.crypt_keys.get('aaaa'))
    # # print(op.forge_keys())
    # # from pprint import pprint
    # # keychain = op.keychain()
    # # pprint(keychain)
    # # print(len(keychain))

    # print('Op pubkey:',op.keychain()['pubkey'])
    # print('Ca pubkey:',ca.keychain()['pubkey'])
