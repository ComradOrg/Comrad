# mine imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade.backend.caller import Caller
from komrade import KomradeException,Logger

# other imports
import asyncio,os,time,sys,logging,getpass
from pythemis.skeygen import KEY_PAIR_TYPE, GenerateKeyPair
from pythemis.smessage import SMessage, ssign, sverify
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal
from base64 import b64decode,b64encode
from pathlib import Path


class Model(Logger): pass

class UserAlreadyExists(KomradeException): pass

class Persona(Model):
    def __init__(self, name, is_group=False):
        self.name = name
        self.is_group=is_group

    @property
    def op(self):
        return Caller(self.name)


    ###
    # MAJOR OPERATIONS
    ###

    def register(self,passphrase = DEBUG_DEFAULT_PASSPHRASE):
        """
        Register this new persona.
        Protect keys according to a passphrase.
        If group, only admin key pass-protected;
        if individual, all keys pass-protected.
        """

        # Does user already exist?
        if self.op.exists(): raise UserAlreadyExists('User already exists')

        # Get passphrase
        if not passphrase: passphrase = getpass.getpass('Enter password for new account: ')
        
        # Create
        if self.is_group:
            self.op.create_keys(adminkey_pass=passphrase)
        else:
            self.op.create_keys(privkey_pass=passphrase,adminkey_pass=passphrase)


    def login(self,passphrase = DEBUG_DEFAULT_PASSPHRASE):
        # Get passphrase
        if not passphrase: passphrase = getpass.getpass('Enter login password: ')
        
        # Get my decryption keys
        if self.is_group:
            keychain_decr = self.op.keychain_decr(adminkey_pass=passphrase)
        else:
            keychain_decr = self.op.keychain_decr(privkey_pass=passphrase,adminkey_pass=passphrase)

        print(keychain_decr)

        




if __name__ == '__main__':
    import random
    idnum = random.choice(list(range(1000)))
    persona = Persona('Op'+str(idnum))
    print('\n\n\nREGISTERING\n\n\n')
    persona.register(passphrase='bb')

    print('\n\n\nLOGGING IN\n\n\n')
    
    persona.login(passphrase='bb')