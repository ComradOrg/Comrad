import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade.backend.crypt import Crypt
# from komrade.backend.the_operator import TheOperator
from komrade.backend.keymaker import Keymaker
from komrade import KomradeException,Logger


from pythemis.skeygen import KEY_PAIR_TYPE, GenerateKeyPair
from pythemis.smessage import SMessage, ssign, sverify
from pythemis.skeygen import GenerateSymmetricKey
from pythemis.scell import SCellSeal
from pythemis.exception import ThemisError
import getpass,os


# paths
PATH_KOMRADE = os.path.abspath(os.path.join(os.path.expanduser('~'),'.komrade'))
PATH_CALLER = os.path.join(PATH_KOMRADE,'.caller')
PATH_CALLER_PUBKEY = os.path.join(PATH_CALLER,'.ca.key.pub.encr')
PATH_CALLER_PRIVKEY = os.path.join(PATH_CALLER,'.ca.key.priv.encr')
PATH_CRYPT_KEYS = os.path.join(PATH_CALLER,'.ca.db.keys.crypt')
PATH_CRYPT_DATA = os.path.join(PATH_CALLER,'.ca.db.data.encr')



# class HelloOperator(object):
#     def __init__(self,op=None):
#         # for now
#         self.op = TheOperator()

#     def create_keys(self,name):
#         return self.op.create_keys(name)

#     def exists(self,*x,**y): return self.op.exists(*x,**y)

if __name__ == '__main__':
    #caller = Caller('elon2')
    Op = Caller()
    # caller.register()