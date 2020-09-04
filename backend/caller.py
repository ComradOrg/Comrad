from pythemis.skeygen import KEY_PAIR_TYPE, GenerateKeyPair
from pythemis.smessage import SMessage, ssign, sverify
from pythemis.skeygen import GenerateSymmetricKey
from pythemis.scell import SCellSeal
from pythemis.exception import ThemisError
import getpass,os
from crypt import Crypt
from the_operator import TheOperator

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


class Caller(object):

    ### INIT CODE
    def __init__(self,name):
        self.name=name
        self.op = TheOperator()

    
    def log(self,*x): print(*x)


    ## CRYPT BASICS

    @property
    def crypt_cell(self):
        pass

    @property
    def crypt_keys(self):
        if not hasattr(self,'_crypt_keys'):
            self._crypt_keys = Crypt(fn=PATH_CRYPT_KEYS)
        return self._crypt_keys

    @property
    def crypt_data(self):
        if not hasattr(self,'_crypt_data'):
            self._crypt_data = Crypt(fn=PATH_CRYPT_DATA)
        return self._crypt_data



    ### CREATION OF KEYS

    # Get key de-cryptors
    def gen_pass_keycell(self,pass_phrase,q_name='Read permissions?'):
        if pass_phrase is None:
            pass_key = GenerateSymmetricKey()
            pass_cell = SCellSeal(key=pass_key)
        else:
            if pass_phrase is True: pass_phrase=getpass.getpass(f'Enter pass phrase [{q_name}]: ')
            pass_key = None
            pass_cell = SCellSeal(passphrase=pass_phrase)
        return (pass_key, pass_cell)

    
    def create_keys(self,pubkey_pass = None, privkey_pass = None, adminkey_pass = None):
        # Get keys back from The Operator
        res = self.op.create_keys(self.name)
        self.log('create_keys() res from Operator? <-',res)
        assert type(res)==tuple and len(res)==3
        (pubkey_decr, privkey_decr, adminkey_decr) = res

        # Get new encryptors
        pubkey_passkey,pubkey_passcell = self.gen_pass_keycell(pubkey_pass,q_name='Permission key, to find')
        privkey_passkey,privkey_passcell = self.gen_pass_keycell(privkey_pass,q_name='Permission key, to read')
        adminkey_passkey,adminkey_passcell = self.gen_pass_keycell(adminkey_pass,q_name='Permission key, to admin')
 
        # double-encrypt what was received
        pubkey_decr_encr = pubkey_passcell.encrypt(pubkey_decr)
        privkey_decr_encr = privkey_passcell.encrypt(privkey_decr)
        adminkey_decr_encr = adminkey_passcell.encrypt(adminkey_decr)

        # store double encrypted keys
        self.crypt_keys.set(self.name,pubkey_decr_encr,prefix='/pub_decr_encr/')
        self.crypt_keys.set(pubkey_decr,privkey_decr_encr,prefix='/priv_decr_encr/')
        self.crypt_keys.set(privkey_decr,adminkey_decr_encr,prefix='/admin_decr_encr/')
        
        # store decryption keys if not passworded?
        if pubkey_passkey: self.crypt_keys.set(self.name,pubkey_passkey,prefix='/pub_decr_decr/')
        if privkey_passkey: self.crypt_keys.set(pubkey_decr,privkey_passkey,prefix='/priv_decr_decr/')
        if adminkey_passkey: self.crypt_keys.set(privkey_decr,adminkey_passkey,prefix='/admin_decr_decr/')
        
        # done?



    ## MAGIC KEY ATTRIBUTES

    @property
    def pubkey_decr_encr(self):
        return self.crypt_keys.get(self.name,prefix='/pub_decr_encr/')
    
    @property
    def privkey_decr_encr(self):
        return self.crypt_keys.get(self.pubkey_decr,prefix='/priv_decr_encr/')
    
    @property
    def pubkey_decr_encr(self):
        return self.crypt_keys.get(self.privkey_decr,prefix='/admin_decr_encr/')
    
    

    
    
    # loading keys back

    @property
    def pubkey_decr_cell(self):
        decr_key = self.crypt_keys.get(self.name,prefix='/pub_decr_encr/')
        if not decr_key:
            if not self.passphrase: return
            decr_cell = SCellSeal(passphrase=self.passphrase)
        else:
            decr_cell = SCellSeal(key=decr_key)
        return decr_cell

    
    @property
    def privkey_decr_cell(self):
        decr_key = self.crypt_keys.get(self.name,prefix='/priv_decr_encr/')
        if not decr_key:
            if not self.passphrase: return
            decr_cell = SCellSeal(passphrase=self.passphrase)
        else:
            decr_cell = SCellSeal(key=decr_key)
        return decr_cell
    
    @property
    def adminkey_decr_cell(self):
        decr_key = self.crypt_keys.get(self.name,prefix='/admin_decr_encr/')
        if not decr_key:
            if not self.passphrase: return
            decr_cell = SCellSeal(passphrase=self.passphrase)
        else:
            decr_cell = SCellSeal(key=decr_key)
        return decr_cell

    @property
    def pubkey_decr(self):
        return self.pubkey_decr_cell.decrypt(self.pubkey_decr_encr)

    @property
    def privkey_decr(self):
        return self.privkey_decr_cell.decrypt(self.privkey_decr_encr)

    @property
    def adminkey_decr(self):
        return self.adminkey_decr_cell.decrypt(self.adminkey_decr_encr)
    
    




    ### HIGH LEVEL
    # Do I exist?

    def exists(self):
        return self.op.exists(self.name)

    def register(self,passphrase = None, as_group=False):
        if self.exists():
            self.log('ERROR: user already exists')
            return

        if not passphrase: passphrase = getpass.getpass('Enter password for new account: ')
        self.passphrase=passphrase

        if as_group:
            self.create_keys(adminkey_pass=passphrase)
        else:
            self.create_keys(privkey_pass=passphrase, adminkey_pass=passphrase)


    def login(self,passphrase = None):
        if not passphrase: passphrase = getpass.getpass('Enter login password: ')
        self.passphrase = passphrase
        if not 



if __name__ == '__main__':
    caller = Caller('elon2')

    caller.register()