import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *



class KomradeSymmetric(SCellSeal):
    @property
    def cell(self):
        if not hasattr(self,'_cell'):
            if hasattr(self,'passphrase') and self.passphrase:
                self._cell = SCellSeal(passphrase=passphrase)
            elif hasattr(self,'key') and self.key:
                self._cell = SCellSeal(key=key)
        
class KomradeSymmetricPass(KomradeSymmetric):
    def __init__(self,passphrase=None, why=WHY_MSG):
        self.passphrase=passphrase
        if not self.passphrase:
            self.passphrase=getpass.getpass(why)
        return self.passphrase

class KomradeSymmetricKey(SCellSeal):
    def __init__(self):
        self.key = GenerateSymmetricKey()


class Keymaker(Logger):
    def __init__(self,name=None,passphrase=None, path_crypt_keys=None, path_crypt_data=None):
        self.name=name
        self.passphrase=passphrase
        self.path_crypt_keys=path_crypt_keys
        self.path_crypt_data=path_crypt_data

        for k in KEYNAMES:
            func = lambda: self.keychain().get(k)
            setattr(self,'_'+k,func) 

    ### BASE STORAGE
    @property
    def crypt_keys(self):
        if not hasattr(self,'_crypt_keys'):
            self._crypt_keys = Crypt(fn=self.path_crypt_keys)
        return self._crypt_keys

    @property
    def crypt_data(self):
        if not hasattr(self,'_crypt_data'):
            self._crypt_data = Crypt(fn=self.path_crypt_data)
        return self._crypt_data


    ### STARTING WITH MOST ABSTRACT

    def findkey(self, keyname, keychain=defaultdict(None), uri=None):
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
            

    def getkey(self, keyname, keychain=defaultdict(None), uri=None):
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
    def pubkey_(self): return self.keychain().get('pubkey')
    @property
    def privkey_(self, **kwargs): return self.keychain().get('privkey')
    @property
    def adminkey_(self, **kwargs): return self.keychain().get('adminkey')
    
    ## (1-X) Encrypted halves
    @property
    def pubkey_encr_(self, **kwargs):return self.keychain().get('pubkey_encr')
    @property
    def privkey_encr_(self, **kwargs): return self.keychain().get('privkey_encr')
    @property
    def adminkey_encr_(self, **kwargs): return self.keychain().get('adminkey_encr')

    ## (1-Y) Decrpytor halves
    @property
    def pubkey_decr_(self, **kwargs): return self.keychain().get('pubkey_decr')
    @property
    def privkey_decr_(self, **kwargs): return self.keychain().get('privkey_decr')
    @property
    def adminkey_decr_(self, **kwargs): return self.keychain().get('adminkey_decr')

    ## Second halving!
    ## (1-X-X)
    @property
    def pubkey_encr_encr_(self, **kwargs): return self.keychain().get('pubkey_encr_encr')
    @property
    def privkey_encr_encr_(self, **kwargs): return self.keychain().get('privkey_encr_encr')
    @property
    def adminkey_encr_encr_(self, **kwargs): return self.keychain().get('adminkey_encr_encr')

    ## (1-X-Y)
    @property
    def pubkey_encr_decr_(self, **kwargs): return self.keychain().get('pubkey_encr_decr')
    @property
    def privkey_encr_decr_(self, **kwargs): return self.keychain().get('privkey_encr_decr')
    @property
    def adminkey_encr_decr_(self, **kwargs): return self.keychain().get('adminkey_encr_decr')

    ## (1-Y-X)
    @property
    def pubkey_decr_encr_(self, **kwargs): return self.keychain().get('pubkey_decr_encr')
    @property
    def privkey_decr_encr_(self, **kwargs): return self.keychain().get('privkey_decr_encr')
    @property
    def adminkey_decr_encr_(self, **kwargs): return self.keychain().get('adminkey_decr_encr')

    ## (1-Y-Y)
    @property
    def pubkey_decr_decr_(self, **kwargs): return self.keychain().get('pubkey_decr_decr')
    @property
    def privkey_decr_decr_(self, **kwargs): return self.keychain().get('privkey_decr_decr')
    @property
    def adminkey_decr_decr_(self, **kwargs): return self.keychain().get('adminkey_decr_decr')


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
    
    def get_new_keys(self):
        raise KomradeException('Every keymaker must make their own get_new_keys() !')

    def gen_keys_from_types(self,key_types,passphrase=None):
        asymmetric_pubkey=None
        asymmetric_privkey=None
        keychain = defaultdict(None)
        for key_name,key_type_descr in key_types.items():
            if key_type_descr in {KEY_TYPE_ASYMMETRIC_PRIVKEY,KEY_TYPE_ASYMMETRIC_PRIVKEY}:
                if not asymmetric_privkey or not asymmetric_pubkey:
                    keypair = GenerateKeyPair(KEY_PAIR_TYPE.EC)
                    asymmetric_privkey = keypair.export_private_key()
                    asymmetric_pubkey = keypair.export_public_key()

            if key_type_descr==KEY_TYPE_ASYMMETRIC_PRIVKEY:
                keychain[key_name] = asymmetric_privkey
            elif key_type_descr==KEY_TYPE_ASYMMETRIC_PUBKEY:
                keychain[key_name] = asymmetric_pubkey
            elif key_type_desc==KEY_TYPE_SYMMETRIC_WITHOUT_PASSPHRASE:
                keychain[key_name]=KomradeSymmetricKey()
            elif key_type_desc==KEY_TYPE_SYMMETRIC_WITH_PASSPHRASE:
                if not passphrase and not self.passphrase:
                    self.passphrase=getpass.getpass(WHY_MSG)
                keychain[key_name]=KomradeSymmetricPass(passphrase=passphrase if passphrase else self.passphrase)


    def forge_new_keys(self,
                        name,
                        keys_to_save = KEYMAKER_DEFAULT_KEYS_TO_SAVE,
                        keys_to_return = KEYMAKER_DEFAULT_KEYS_TO_RETURN,
                        key_types = KEYMAKER_DEFAULT_KEY_TYPES):
        self.log('forging new keys...')

        # Create public and private keys
        keychain = {}
        keypair = GenerateKeyPair(KEY_PAIR_TYPE.EC)
        keychain['privkey'] = keypair.export_private_key()
        keychain['pubkey'] = keypair.export_public_key()
        keychain['adminkey'] = GenerateSymmetricKey()

        # # Create decryption/permission keys
        # keychain['pubkey_decr'] = GenerateSymmetricKey()
        # keychain['privkey_decr'] = GenerateSymmetricKey()
        # keychain['adminkey_decr'] = GenerateSymmetricKey() #SCellSeal(passphrase=passphrase)
        
        # # Encrypt original keys
        # keychain['pubkey_encr'] = SCellSeal(key=pubkey_decr).encrypt(pubkey)
        # keychain['privkey_encr'] = SCellSeal(key=privkey_decr).encrypt(privkey)
        # keychain['adminkey_encr'] = SCellSeal(key=adminkey_decr).encrypt(adminkey)

        double_enc = ['pubkey_decr_encr','pubkey_encr_encr','pubkey_decr_encr','pubkey_encr_encr','pubkey_decr_encr','pubkey_encr_encr']
        for xkey in double_encr:
            if xkey in to_return or xkey in to_save:
                xkey_orig = xkey[:-len('_encr')]
                keychain[xkey] = self.cell_dblencr.encrypt(**)

        # store encrypted on my hardware
        if save_encrypted:
            self.crypt_keys.set(name,pubkey_encr,prefix='/pubkey_encr/')
            self.crypt_keys.set(pubkey,privkey_encr,prefix='/privkey_encr/')
            self.crypt_keys.set(privkey,adminkey_encr,prefix='/adminkey_encr/')

        # store permissions file?
        secret_admin_val = pubkey_encr + BSEP + b'find,read,admin'
        if pubkey_is_public: secret_admin_val += b'*'+BSEP+b'find'
        secret_admin_val_encr = SCellSeal(key=adminkey).encrypt(secret_admin_val)
        if save_encrypted:
            self.crypt_keys.set(adminkey,secret_admin_val_encr,prefix='/permkey_encr/')

            # keep public key?
        if pubkey_is_public:
            self.crypt_keys.set(name,pubkey_decr,prefix='/pubkey_decr/')
        
        # send back decryption keys to client
        toreturn={}
        if return_decrypted:
            toreturn['pubkey_decr']=pubkey_decr
            toreturn['privkey_decr']=privkey_decr
            toreturn['adminkey_decr']=adminkey_decr
        
        if return_encrypted:   
            toreturn['pubkey_encr']=pubkey_encr
            toreturn['privkey_encr']=privkey_encr
            toreturn['adminkey_encr']=adminkey_encr
         
        return toreturn
        
    @property
    def cell_dblencr(self):
        if not hasattr(self,'_cell_dblencr'):
            self._dbl_encr = get_cell_dblencr()
        return self._dbl_encr

    def get_cell_dblencr(self,passphrase=None):
        if not passphrase:
            if self.passphrase:
                passphrase=self.passphrase
            else:
                self.passphrase=passphrase=getpass.getpass('Forge the password of memory: ')
        cell = SCellSeal(passphrase=passphrase)
        return cell

        
    def lock_new_keys(self,
                        keychain,
                        passphrase=None,
                        save_encrypted = True, return_encrypted = False,
                        save_decrypted = False, return_decrypted = True):
        # we're not going to store the decryptor keys directly though
        

        # encrypt the decryptor keys
        pubkey_decr_encr = cell.encrypt(keychain['pubkey_decr'])
        privkey_decr_encr = cell.encrypt(keychain['privkey_decr'])
        adminkey_decr_encr = cell.encrypt(keychain['adminkey_decr'])
        
        # set to crypt and keychain
        if save_decrypted:
            self.crypt_keys.set(self.name,pubkey_decr_encr,prefix='/pubkey_decr_encr/')
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
        