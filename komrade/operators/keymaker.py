import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.operators.crypt import *

class Keymaker(Logger):
    def __init__(self,name=None,passphrase=None):
        self.name=name
        self.passphrase=passphrase

        for k in KEYNAMES:
            func = lambda: self.keychain().get(k)
            setattr(self,'_'+k,func) 

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
        self.log(f'looking for key {keyname}, in keychain {keychain.keys()} or under crypt uri {uri}')
        # look in keychain, then in crypt, for this key
        given_key = keychain.get(keyname)
        if given_key:
            self.log(f'{keyname} found in keychain: {given_key}')
            return given_key

        found_key = self.crypt_keys.get(uri,prefix=f'/{keyname}/')
        if found_key:
            self.log(f'{keyname} found in crypt: {given_key}')
            return found_key

        self.log(f'{keyname} not found!!')
            

    def getkey(self, keyname, keychain={}, uri=None):
        self.log(f'keyname={keyname}, keychain={keychain.keys()}, uri={uri}')

        # 1) I already have this key stored in either the keychain or the crypt; return straight away
        key = self.findkey(keyname, keychain, uri)
        if key:
            self.log(f'>> I have {key} already, returning')
            return key

        ## 2) I can assemble the key
        self.log(f'assembling key: {keyname}_encr + {keyname}_decr')
        key_encr = self.findkey(keyname+'_encr', keychain,uri)
        key_decr = self.findkey(keyname+'_decr', keychain, uri)
        key = self.assemble_key(key_encr, key_decr)
        return key

    def get_cell(self, str_or_key_or_cell):
        self.log('getting decr cell for',str_or_key_or_cell)

        if type(str_or_key_or_cell)==SCellSeal:
            return str_or_key_or_cell
        elif type(str_or_key_or_cell)==str:
            return SCellSeal(passphrase=str_or_key_or_cell)
        elif type(str_or_key_or_cell)==bytes:
            return SCellSeal(key=str_or_key_or_cell)

    def assemble_key(self, key_encr, key_decr):
        self.log(f'assembling key: {key_decr} decrypting {key_encr}')

        # need the encrypted half
        if not key_encr:
            self.log('!! encrypted half not given')
            return
        if not key_decr:
            if self.passphrase:
                key_decr = self.passphrase
            else:
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
            self.log(f'>> decrypting {key_encr} with cell {decr_cell}')
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
        return self.getkey(uri=self.pubkey(**kwargs),keyname='privkey_encr',**kwargs)
    def adminkey_encr(self, **kwargs):
        return self.getkey(uri=self.privkey(**kwargs),keyname='adminkey_encr',**kwargs)

    ## (1-Y) Decrpytor halves
    def pubkey_decr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_decr',**kwargs)
    def privkey_decr(self, **kwargs):
        return self.getkey(uri=self.pubkey(**kwargs),keyname='privkey_decr',**kwargs)
    def adminkey_decr(self, **kwargs):
        return self.getkey(uri=self.privkey(**kwargs),keyname='adminkey_decr',**kwargs)

    ## Second halving!
    ## (1-X-X)
    def pubkey_encr_encr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_encr_encr',**kwargs)
    def privkey_encr_encr(self, **kwargs):
        return self.getkey(uri=self.pubkey_encr(**kwargs),keyname='privkey_encr_encr',**kwargs)
    def adminkey_encr_encr(self, **kwargs):
        return self.getkey(uri=self.privkey_encr(**kwargs),keyname='adminkey_encr_encr',**kwargs)

    ## (1-X-Y)
    def pubkey_encr_decr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_encr_decr',**kwargs)
    def privkey_encr_decr(self, **kwargs):
        return self.getkey(uri=self.pubkey_encr(**kwargs),keyname='privkey_encr_decr',**kwargs)
    def adminkey_encr_decr(self, **kwargs):
        return self.getkey(uri=self.privkey_encr(**kwargs),keyname='adminkey_encr_decr',**kwargs)

    ## (1-Y-X)
    def pubkey_decr_encr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_decr_encr',**kwargs)
    def privkey_decr_encr(self, **kwargs):
        return self.getkey(uri=self.pubkey_decr(**kwargs),keyname='privkey_decr_encr',**kwargs)
    def adminkey_decr_encr(self, **kwargs):
        return self.getkey(uri=self.privkey_decr(**kwargs),keyname='adminkey_decr_encr',**kwargs)

    ## (1-Y-Y)
    def pubkey_decr_decr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_decr_decr',**kwargs)
    def privkey_decr_decr(self, **kwargs):
        return self.getkey(uri=self.pubkey_decr(**kwargs),keyname='privkey_decr_decr',**kwargs)
    def adminkey_decr_decr(self, **kwargs):
        return self.getkey(uri=self.privkey_decr(**kwargs),keyname='adminkey_decr_decr',**kwargs)


    # convenience functions
    
    # Concrete keys
    @property
    def pubkey__(self): return self.keychain()['pubkey']
    @property
    def privkey_(self, **kwargs): return self.keychain()['privkey']
    @property
    def adminkey_(self, **kwargs): return self.keychain()['adminkey']
    
    ## (1-X) Encrypted halves
    @property
    def pubkey_encr_(self, **kwargs):return self.keychain()['pubkey_encr']
    @property
    def privkey_encr_(self, **kwargs): return self.keychain()['privkey_encr']
    @property
    def adminkey_encr_(self, **kwargs): return self.keychain()['adminkey_encr']

    ## (1-Y) Decrpytor halves
    @property
    def pubkey_decr_(self, **kwargs): return self.keychain()['pubkey_decr']
    @property
    def privkey_decr_(self, **kwargs): return self.keychain()['privkey_decr']
    @property
    def adminkey_decr_(self, **kwargs): return self.keychain()['adminkey_decr']

    ## Second halving!
    ## (1-X-X)
    @property
    def pubkey_encr_encr_(self, **kwargs): return self.keychain()['pubkey_encr_encr']
    @property
    def privkey_encr_encr_(self, **kwargs): return self.keychain()['privkey_encr_encr']
    @property
    def adminkey_encr_encr_(self, **kwargs): return self.keychain()['adminkey_encr_encr']

    ## (1-X-Y)
    @property
    def pubkey_encr_decr_(self, **kwargs): return self.keychain()['pubkey_encr_decr']
    @property
    def privkey_encr_decr_(self, **kwargs): return self.keychain()['privkey_encr_decr']
    @property
    def adminkey_encr_decr_(self, **kwargs): return self.keychain()['adminkey_encr_decr']

    ## (1-Y-X)
    @property
    def pubkey_decr_encr_(self, **kwargs): return self.keychain()['pubkey_decr_encr']
    @property
    def privkey_decr_encr_(self, **kwargs): return self.keychain()['privkey_decr_encr']
    @property
    def adminkey_decr_encr_(self, **kwargs): return self.keychain()['adminkey_decr_encr']

    ## (1-Y-Y)
    @property
    def pubkey_decr_decr_(self, **kwargs): return self.keychain()['pubkey_decr_decr']
    @property
    def privkey_decr_decr_(self, **kwargs): return self.keychain()['privkey_decr_decr']
    @property
    def adminkey_decr_decr_(self, **kwargs): return self.keychain()['adminkey_decr_decr']


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
        keychain = self.forge_new_keys(self.name)
        self.log('create_keys() res from Operator? <-',keychain)

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
        

        
    def lock_new_keys(self,keychain,passphrase=None):
        # we're not going to store the decryptor keys directly though
        if not passphrase:
            if self.passphrase:
                passphrase=self.passphrase
            else:
                self.passphrase=passphrase=getpass.getpass('Forge the password of memory: ')
        
        cell = SCellSeal(passphrase=passphrase)

        # encrypt the decryptor keys
        pubkey_decr_encr = cell.encrypt(keychain['pubkey_decr'])
        privkey_decr_encr = cell.encrypt(keychain['privkey_decr'])
        adminkey_decr_encr = cell.encrypt(keychain['adminkey_decr'])
        
        # set to crypt and keychain
        self.crypt_keys.set(self.name,pubkey_decr_encr,prefix='/pubkey_decr_encr/')
        #keychain['pubkey_decr_encr']=pubkey_decr_encr
        
        self.crypt_keys.set(keychain['pubkey_decr'],privkey_decr_encr,prefix='/privkey_decr_encr/')
        #keychain['privkey_decr_encr']=privkey_decr_encr
        
        self.crypt_keys.set(keychain['privkey_decr'],adminkey_decr_encr,prefix='/adminkey_decr_encr/')
        #keychain['adminkey_decr_encr']=adminkey_decr_encr
        
        # store decryption keys if not passworded?
        pub_ddk,priv_ddk,admin_ddk=[x+'key_decr_decr_key' for x in ['pub','priv','admin']]
        if pub_ddk in keychain:
            self.crypt_keys.set(self.name, keychain[pub_ddk], prefix=f'/{pub_ddk}/')
        if priv_ddk in keychain:
            self.crypt_keys.set(self.name, keychain[priv_ddk], prefix=f'/{priv_ddk}/')
        if admin_ddk in keychain:
            self.crypt_keys.set(self.name, keychain[admin_ddk], prefix=f'/{admin_ddk}/')
        
        # # return protected keychain
        # todel = ['pubkey_decr','privkey_decr','adminkey_decr']
        # for x in todel:
        #     if x in keychain:
        #         del keychain[x]

        # # add encr versions
        # keychain

        # del keychain['pubkey_decr']
        # del keychain['privkey_decr']
        # del keychain['adminkey_decr']
        

        # return ()
        return passphrase

    # def load_concrete_keychain():
    #     keychain = {}
    #     for keyname in KEYNAMES:
    #         keychain=self.findkey(keyname, keychain, uri)

    def keychain(self,passphrase=None,force=False,**kwargs):
        # assemble as many keys as we can!
        if not force and hasattr(self,'_keychain') and self._keychain: return self._keychain
        if passphrase: self.passphrase=passphrase


        _keychain = defaultdict(None)
        for keyname in reversed(KEYNAMES+KEYNAMES):
            self.log('??',keyname,'...')
            if hasattr(self,keyname):
                method=getattr(self,keyname)
                res=method(keychain=_keychain, **kwargs)
                self.log('res <--',res)
                if res:
                    _keychain[keyname]=res
        return _keychain
        