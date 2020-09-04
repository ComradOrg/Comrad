from komrade.backend.crypt import Crypt
from komrade import KomradeException,Logger
from pythemis.skeygen import KEY_PAIR_TYPE, GenerateKeyPair
from pythemis.smessage import SMessage, ssign, sverify
from pythemis.skeygen import GenerateSymmetricKey
from pythemis.scell import SCellSeal
from pythemis.exception import ThemisError
import getpass,os

PATH_KOMRADE = os.path.abspath(os.path.join(os.path.expanduser('~'),'.komrade'))
PATH_OPERATOR = os.path.join(PATH_KOMRADE,'.operator')
PATH_OPERATOR_PUBKEY = os.path.join(PATH_OPERATOR,'.op.key.pub.encr')
PATH_OPERATOR_PRIVKEY = os.path.join(PATH_OPERATOR,'.op.key.priv.encr')
PATH_CRYPT_KEYS = os.path.join(PATH_OPERATOR,'.op.db.keys.crypt')
PATH_CRYPT_DATA = os.path.join(PATH_OPERATOR,'.op.db.data.encr')

class Keymaker(Logger):
    ### BASE STORAGE
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


    ### STARTING WITH MOST ABSTRACT

    def findkey(self, keyname, keychain={}, uri=None):
        # look in keychain, then in crypt, for this key
        given_key = keychain.get(keyname)
        if given_key: return given_key

        found_key = self.crypt_keys.get(uri,prefix=f'/{keyname}/')
        if found_key: return found_key

    def getkey(self, keyname, keychain={}, uri=None):
        # 1) I already have this key stored in either the keychain or the crypt; return straight away
        key = self.findkey(keyname, keychain, uri)
        if key: return key

        ## 2) I can assemble the key
        key_encr = self.findkey(keyname+'_encr', keychain,uri)
        key_decr = self.findkey(keyname+'_decr', keychain, uri)
        key = self.assemble_key(key_encr, key_decr)
        return key

    def get_cell(self, str_or_key_or_cell):
        if type(str_or_key_or_cell)==SCellSeal:
            return str_or_key_or_cell
        elif type(str_or_key_or_cell)==str:
            return SCellSeal(passphrase=str_or_key_or_cell)
        elif type(str_or_key_or_cell)==bytes:
            return SCellSeal(key=key)

    def assemble_key(self, key_encr, key_decr):
        # need the encrypted half
        if not key_encr:
            self.log('!! encrypted half not given')
            return
        if not key_decr:
            self.log('!! decryptor half not given')
            return

        # need some way to regenerate the decryptor
        decr_cell = self.get_cell(key_decr)

        # need the decryptor half
        if not decr_cell:
            self.log('!! decryptor cell not regenerable')
            return

        # decrypt!
        try:
            key = decr_cell.decrypt(key_encr)
            self.log('assembled_key built:',key)
            return key
        except ThemisError as e:
            self.log('!! decryption failed:',e)


    # Concrete keys
    ## (1) Final keys
    def pubkey(self, **kwargs):
        return self.getkey(keyname='pubkey',uri=self.name,**kwargs)
    def privkey(self, **kwargs):
        return self.getkey(keyname='privkey',uri=self.pubkey(**kwargs),**kwargs)
    def adminkey(self, **kwargs):
        return self.getkey(keyname='adminkey',uri=self.privkey(**kwargs),**kwargs)
    
    ## (1-X) Encrypted halves
    def pubkey_encr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_encr',**kwargs)
    def privkey_encr(self, **kwargs):
        return self.getkey(uri=self.pubkey_encr(**kargs),keyname='privkey_encr',**kwargs)
    def adminkey_encr(self, **kwargs):
        return self.getkey(uri=self.privkey_encr(**kargs),keyname='adminkey_encr',**kwargs)

    ## (1-Y) Decrpytor halves
    def pubkey_decr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_decr',**kwargs)
    def privkey_decr(self, **kwargs):
        return self.getkey(uri=self.pubkey_decr(**kargs),keyname='privkey_decr',**kwargs)
    def adminkey_decr(self, **kwargs):
        return self.getkey(uri=self.privkey_decr(**kargs),keyname='adminkey_decr',**kwargs)

    ## Second halving!
    ## (1-X-X)
    def pubkey_encr_encr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_encr_encr',**kwargs)
    def privkey_encr_encr(self, **kwargs):
        return self.getkey(uri=self.pubkey_encr_encr(**kargs),keyname='privkey_encr_encr',**kwargs)
    def adminkey_encr_encr(self, **kwargs):
        return self.getkey(uri=self.privkey_encr_encr(**kargs),keyname='adminkey_encr_encr',**kwargs)

    ## (1-X-Y)
    def pubkey_encr_decr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_encr_decr',**kwargs)
    def privkey_encr_decr(self, **kwargs):
        return self.getkey(uri=self.pubkey_encr_decr(**kargs),keyname='privkey_encr_decr',**kwargs)
    def adminkey_encr_decr(self, **kwargs):
        return self.getkey(uri=self.privkey_encr_decr(**kargs),keyname='adminkey_encr_decr',**kwargs)

    ## (1-Y-X)
    def pubkey_decr_encr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_decr_encr',**kwargs)
    def privkey_decr_encr(self, **kwargs):
        return self.getkey(uri=self.pubkey_decr_encr(**kargs),keyname='privkey_decr_encr',**kwargs)
    def adminkey_decr_encr(self, **kwargs):
        return self.getkey(uri=self.privkey_decr_encr(**kargs),keyname='adminkey_decr_encr',**kwargs)

    ## (1-Y-Y)
    def pubkey_decr_decr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_decr_decr',**kwargs)
    def privkey_decr_decr(self, **kwargs):
        return self.getkey(uri=self.pubkey_decr_decr(**kargs),keyname='privkey_decr_decr',**kwargs)
    def adminkey_decr_decr(self, **kwargs):
        return self.getkey(uri=self.privkey_decr_decr(**kargs),keyname='adminkey_decr_decr',**kwargs)

    ### DECR ENCR KEYS
    ## Third level: splitting (encrypted/decryption key) the encrypted keys and decryption keys above

    

    # Get key de-cryptors
    def genkey_pass_keycell(self,pass_phrase,q_name='Read permissions?'):
        if pass_phrase is None:
            pass_key = GenerateSymmetricKey()
            pass_cell = SCellSeal(key=pass_key)
        else:
            if pass_phrase is True: pass_phrase=getpass.getpass(f'Enter pass phrase [{q_name}]: ')
            pass_key = None
            pass_cell = SCellSeal(passphrase=pass_phrase)

        self.log(f'pass_key [{q_name}] <--',pass_key)
        self.log(f'pass_cell [{q_name}] <--',pass_cell)
        return (pass_key, pass_cell)



    def exists(self):
        return self.crypt_keys.exists(self.name,prefix='/pubkey_encr/') or self.crypt_keys.exists(self.name,prefix='/pubkey_decr/') or self.crypt_keys.exists(self.name,prefix='/pubkey/')

    ### CREATING KEYS
    
    def get_new_keys(self,pubkey_pass = None, privkey_pass = None, adminkey_pass = None):
        # Get decryptor keys back from The Operator (one half of the Keymaker)
        keychain = self.forge_keys(self.name)
        self.log('create_keys() res from Operator? <-',res)

        # Now lock the decryptor keys away, sealing it with a password of memory!
        self.lock_new_keys(keychain)

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
