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


class Caller(Keymaker):
    PATH_CRYPT_KEYS=PATH_CRYPT_KEYS
    PATH_CRYPT_DATA=PATH_CRYPT_DATA

    ### INIT CODE
    def __init__(self,name):
        self.name=name
        # self.op = TheOperator()

    ## CRYPT BASICS

    @property
    def crypt_cell(self):
        pass

    ### CREATION OF KEYS
    # def exists(self):
        # return self.op.exists(self.name)

    def get_new_keys(self,pubkey_pass = None, privkey_pass = None, adminkey_pass = None):
        # Get keys back from The Operator
        keychain = self.op.forge_keys(self.name)
        self.log('create_keys() res from Operator? <-',res)
        
    def lock_new_keys(self,keychain):
        # we're not going to store the decryptor keys directly though
        passphrase=getpass.getpass('Forge the password of memory: ')
        cell = SCellSeal(passphrase=passphrase)
        # encrypt the decryptor keys
        pubkey_decr_encr = cell.encrypt(keychain['pubkey_decr'])
        privkey_decr_encr = cell.encrypt(keychain['privkey_decr'])
        adminkey_decr_encr = cell.encrypt(keychain['adminkey_decr'])
        
        # set to crypt, like a caller
        self.crypt_keys.set(self.name,pubkey_decr_encr,prefix='/pubkey_decr_encr/')
        self.crypt_keys.set(keychain['pubkey_decr'],privkey_decr_encr,prefix='/privkey_decr_encr/')
        self.crypt_keys.set(keychain['privkey_decr'],adminkey_decr_encr,prefix='/adminkey_decr_encr/')
        
        lock_keys_

        assert type(res)==tuple and len(res)==3
        (pubkey_decr, privkey_decr, adminkey_decr) = res

        # double-encrypt what was received
        pubkey_decr_decr_key,pubkey_decr_decr_cell = self.pubkey_decr_decr_keycell(passphrase=pubkey_pass)
        self.log('pubkey_decr_decr_key <--',pubkey_decr_decr_key)
        self.log('pubkey_decr_decr_cell <--',pubkey_decr_decr_cell)
        self.log('pubkey_decr <--',pubkey_decr)
        pubkey_decr_encr = pubkey_decr_decr_cell.encrypt(pubkey_decr)
        self.log('pubkey_decr_encr <--',pubkey_decr_encr)

        # privkey_decr_encr = privkey_passcell.encrypt(privkey_decr)
        # self.log('pubkey_decr_encr <--',pubkey_decr_encr)

        # adminkey_decr_encr = adminkey_passcell.encrypt(adminkey_decr)
        # self.log('pubkey_decr_encr <--',pubkey_decr_encr)

        # store double encrypted keys
        self.crypt_keys.set(self.name,pubkey_decr_encr,prefix='/pubkey_decr_encr/')
        # self.crypt_keys.set(pubkey_decr,privkey_decr_encr,prefix='/privkey_decr_encr/')
        # self.crypt_keys.set(privkey_decr,adminkey_decr_encr,prefix='/adminkey_decr_encr/')
        
        # store decryption keys if not passworded?
        if pubkey_decr_decr_key: self.crypt_keys.set(self.name,pubkey_decr_decr_key,prefix='/pubkey_decr_decr_key/')
        # if privkey_passkey: self.crypt_keys.set(pubkey_decr,privkey_passkey,prefix='/privkey_decr_decr_key/')
        # if adminkey_passkey: self.crypt_keys.set(privkey_decr,adminkey_passkey,prefix='/adminkey_decr_decr_key/')
        
        # done?



if __name__ == '__main__':
    #caller = Caller('elon2')
    Op = Caller()
    # caller.register()