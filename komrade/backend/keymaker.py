import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *
from abc import ABC, abstractmethod
 
class KomradeKey(ABC):
    @abstractmethod
    def encrypt(self,msg,**kwargs): pass
    @abstractmethod
    def decrypt(self,msg,**kwargs): pass

    @abstractmethod
    def data(self): pass


class KomradeSymmetricKey(KomradeKey):
    @property
    def cell(self):
        if not hasattr(self,'_cell'):
            if hasattr(self,'passphrase') and self.passphrase:
                self._cell = SCellSeal(passphrase=self.passphrase)
            elif hasattr(self,'key') and self.key:
                self._cell = SCellSeal(key=self.key)
        return self._cell
    def encrypt(self,msg,**kwargs):
        if issubclass(type(msg), KomradeKey): msg=msg.data
        return self.cell.encrypt(msg,**kwargs)
    def decrypt(self,msg,**kwargs):
        return self.cell.decrypt(msg,**kwargs)
    
    


        
class KomradeSymmetricKeyWithPassphrase(KomradeSymmetricKey):
    def __init__(self,passphrase=None, why=WHY_MSG):
        self.passphrase=passphrase
        if not self.passphrase:
            self.passphrase=getpass.getpass(why)
        #return self.passphrase
    @property
    def data(self): return KEY_TYPE_SYMMETRIC_WITH_PASSPHRASE.encode('utf-8')

class KomradeSymmetricKeyWithoutPassphrase(KomradeSymmetricKey):
    def __init__(self):
        self.key = GenerateSymmetricKey()
    @property
    def data(self): return self.key



class KomradeAsymmetricKey(KomradeKey):
    def __init__(self,pubkey,privkey):
        self.pubkey=pubkey
        self.privkey=privkey
    def encrypt(self,msg,pubkey=None,privkey=None):
        if issubclass(type(msg), KomradeKey): msg=msg.data
        pubkey=pubkey if pubkey else self.pubkey
        privkey=privkey if privkey else self.privkey
        return SMessage(privkey,pubkey).wrap(msg)
    def decrypt(self,msg,pubkey=None,privkey=None):
        pubkey=pubkey if pubkey else self.pubkey
        privkey=privkey if privkey else self.privkey
        return SMessage(privkey,pubkey).unwrap(msg)
    @property
    def data(self): return self.key

class KomradeAsymmetricPublicKey(KomradeAsymmetricKey):
    @property
    def key(self): return self.pubkey
class KomradeAsymmetricPrivateKey(KomradeAsymmetricKey):
    @property
    def key(self): return self.privkey


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
    def crypt_keys_mem(self):
        if not hasattr(self,'_crypt_keys_mem'):
            self._crypt_keys_mem = CryptMemory()
        return self._crypt_keys_mem
        
    @property
    def crypt_data(self):
        if not hasattr(self,'_crypt_data'):
            self._crypt_data = Crypt(fn=self.path_crypt_data)
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
        keychain = {}
        for key_name,key_type_desc in key_types.items():
            if key_type_desc in {KEY_TYPE_ASYMMETRIC_PUBKEY,KEY_TYPE_ASYMMETRIC_PRIVKEY}:
                if not asymmetric_privkey or not asymmetric_pubkey:
                    keypair = GenerateKeyPair(KEY_PAIR_TYPE.EC)
                    asymmetric_privkey = keypair.export_private_key()
                    asymmetric_pubkey = keypair.export_public_key()

            if key_type_desc==KEY_TYPE_ASYMMETRIC_PRIVKEY:
                keychain[key_name] = KomradeAsymmetricPrivateKey(asymmetric_pubkey,asymmetric_privkey)
            elif key_type_desc==KEY_TYPE_ASYMMETRIC_PUBKEY:
                keychain[key_name] = KomradeAsymmetricPublicKey(asymmetric_pubkey,asymmetric_privkey)
            elif key_type_desc==KEY_TYPE_SYMMETRIC_WITHOUT_PASSPHRASE:
                keychain[key_name]=KomradeSymmetricKeyWithoutPassphrase()
            elif key_type_desc==KEY_TYPE_SYMMETRIC_WITH_PASSPHRASE:
                if not passphrase and not self.passphrase: self.passphrase=getpass.getpass(WHY_MSG)
                passphrase=passphrase if passphrase else self.passphrase
                keychain[key_name]=KomradeSymmetricKeyWithPassphrase(passphrase=passphrase)
        return keychain


    def forge_new_keys(self,
                        name=None,
                        keys_to_save = KEYMAKER_DEFAULT_KEYS_TO_SAVE,
                        keys_to_return = KEYMAKER_DEFAULT_KEYS_TO_RETURN,
                        keys_to_gen = KEYMAKER_DEFAULT_KEYS_TO_GEN,
                        key_types = KEYMAKER_DEFAULT_KEY_TYPES):
        self.log('forging new keys...',name,self.name)
        self.log('keys_to_save:',keys_to_save)
        self.log('keys_to_return',keys_to_return)
        # stop


        if not name: name=self.name

        keys_to_gen = set(keys_to_gen) | set(keys_to_save) | set(keys_to_return)
        keys_to_gen = sorted(list(keys_to_gen),key=lambda x: x.count('_'))
        self.log('keys_to_gen =',keys_to_gen)
        key_types = dict([(k,key_types[k]) for k in keys_to_gen])
        self.log('key_types =',key_types)

        keychain = self.gen_keys_from_types(key_types)
        self.log('keychain =',keychain)

        self.log('!!!!',keychain)
        # stop
        #keychain_tosave = {}
        #keychain_toreturn = {}
        self.log('keys_to_save =',keys_to_save)
        self.log('keys_to_return =',keys_to_return)
        
        for key_name in keys_to_gen:
            if key_name.endswith('_encr') and key_name not in keychain:
                # encrypt it with the associated decr
                name_of_what_to_encrypt = key_name[:-len('_encr')]
                the_key_to_encrypt_it_with = name_of_what_to_encrypt + '_decr'
                if the_key_to_encrypt_it_with in keychain and name_of_what_to_encrypt in keychain:
                    _key_decr = keychain[the_key_to_encrypt_it_with]
                    _key = keychain[name_of_what_to_encrypt]
                    self.log(f'about to encrypt key {name_of_what_to_encrypt}, using {the_key_to_encrypt_it_with}, which is a type {key_types[the_key_to_encrypt_it_with]} and has value {keychain[the_key_to_encrypt_it_with]}')
                    _key_encr = _key_decr.encrypt(_key)
                    self.log(f'{_key}\n-- encrypting ----->\n{_key_encr}')
                    keychain[key_name]=_key_encr
        
        self.log('once more, with encryption!',keychain)

        # filter for transfer
        for k,v in keychain.items():
            if issubclass(type(v),KomradeKey):
                v=v.data
            v=b64encode(v)
            keychain[k]=v
            self.log('-->',v)
            # stop

        # keychain_tosave = dict([(k,keychain[k]) for k in keys_to_save if k in keychain])
        

        # for k,v in keychain_tosave.items():
        if 'pubkey' in keys_to_save or 'privkey' in keys_to_save or 'adminkey' in keys_to_save:
            raise KomradeException('there is no private property in a socialist network! all keys must be split between komrades')

        ### SAVE ENCRYPTED KEYS?
        if 'pubkey_encr' in keys_to_save:
            self.crypt_keys.set(name,keychain['pubkey_encr'],prefix='/pubkey_encr/')
        if 'privkey_encr' in keys_to_save:
            self.crypt_keys.set(keychain['pubkey'],keychain['privkey_encr'],prefix='/privkey_encr/')
        if 'adminkey_encr' in keys_to_save:
            self.crypt_keys.set(keychain['privkey'],keychain['adminkey_encr'],prefix='/adminkey_encr/')

        # save decrypted keys?
        if 'pubkey_decr' in keys_to_save:
            self.crypt_keys.set(name,keychain['pubkey_decr'],prefix='/pubkey_decr/')
        if 'privkey_decr' in keys_to_save:
            self.crypt_keys.set(keychain['pubkey'],keychain['privkey_decr'],prefix='/privkey_decr/')
        if 'adminkey_decr' in keys_to_save:
            self.crypt_keys.set(keychain['privkey'],keychain['adminkey_decr'],prefix='/adminkey_decr/')



        if 'pubkey_encr_encr' in keys_to_save:
            self.crypt_keys.set(name,keychain['pubkey_decr_encr'],prefix='/pubkey_decr_encr/')
        if 'privkey_encr_encr' in keys_to_save:
            self.crypt_keys.set(keychain['pubkey_decr'],keychain['privkey_decr_encr'],prefix='/privkey_decr_encr/')
        if 'adminkey_encr_encr' in keys_to_save:
            self.crypt_keys.set(keychain['privkey_decr'],keychain['adminkey_decr_encr'],prefix='/adminkey_decr_encr/')
        if 'pubkey_decr_encr' in keys_to_save:
            self.crypt_keys.set(name,keychain['pubkey_decr_encr'],prefix='/pubkey_decr_encr/')
        if 'privkey_decr_encr' in keys_to_save:
            self.crypt_keys.set(keychain['pubkey_decr'],keychain['privkey_decr_encr'],prefix='/privkey_decr_encr/')
        if 'adminkey_decr_encr' in keys_to_save:
            self.crypt_keys.set(keychain['privkey_decr'],keychain['adminkey_decr_encr'],prefix='/adminkey_decr_encr/')
        
        if 'pubkey_decr_decr' in keys_to_save:
            self.crypt_keys.set(name,keychain['pubkey_decr_decr'],prefix='/pubkey_decr_decr/')
        if 'privkey_decr_decr' in keys_to_save:
            self.crypt_keys.set(keychain['pubkey_decr'],keychain['privkey_decr_decr'],prefix='/privkey_decr_decr/')
        if 'adminkey_decr_decr' in keys_to_save:
            self.crypt_keys.set(keychain['privkey_decr'],keychain['adminkey_decr_decr'],prefix='/adminkey_decr_decr/')
        if 'pubkey_decr_decr' in keys_to_save:
            self.crypt_keys.set(name,keychain['pubkey_decr_decr'],prefix='/pubkey_decr_decr/')
        if 'privkey_decr_decr' in keys_to_save:
            self.crypt_keys.set(keychain['pubkey_decr'],keychain['privkey_decr_decr'],prefix='/privkey_decr_decr/')
        if 'adminkey_decr_decr' in keys_to_save:
            self.crypt_keys.set(keychain['privkey_decr'],keychain['adminkey_decr_decr'],prefix='/adminkey_decr_decr/')


                
        keychain_toreturn = {}
        for key in keys_to_return:
            if key in keychain:
                print('adding',key,'to returned keychain')
                keychain_toreturn[key]=keychain[key]

        return keychain_toreturn


        
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

        
        _keychain = {}
        
        # am I a builtin one?
        self.log('hello///',self.name,self.name in BUILTIN_KEYCHAIN)
        if self.name in BUILTIN_KEYCHAIN:
            for k,v in BUILTIN_KEYCHAIN[self.name].items():
                _keychain[k]=v
        
        self.log('_keychain',_keychain)
        # stop
        
        for keyname in reversed(KEYNAMES+KEYNAMES):
            self.log('??',keyname,'...')
            if hasattr(self,keyname):
                method=getattr(self,keyname)
                res=method(keychain=_keychain, **kwargs)
                self.log('res <--',res)
                if res:
                    _keychain[keyname]=res
        return _keychain
        


if __name__ == '__main__':
    keymaker = Keymaker('marx69')
    keychain = keymaker.forge_new_keys()

    print(keychain)