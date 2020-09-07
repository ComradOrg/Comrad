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
    def __init__(self,key=None):
        self.key = GenerateSymmetricKey() if not key else key
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
    def __init__(self,name=None,passphrase=None,keychain={}, path_crypt_keys=None, path_crypt_data=None, allow_builtin=True):
        self.name=name
        self._keychain=keychain
        self.passphrase=passphrase
        self.path_crypt_keys=path_crypt_keys
        self.path_crypt_data=path_crypt_data
        self.allow_builtin=allow_builtin


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
        # self.log(f'looking for key {keyname}, in keychain {keychain.keys()} or under crypt uri {uri}')
        # look in keychain, then in crypt, for this key
        given_key = keychain.get(keyname)
        if given_key:
            # self.log(f'{keyname} found in keychain: {given_key}')
            return given_key

        found_key = self.crypt_keys.get(uri,prefix=f'/{keyname}/')
        if found_key:
            # self.log(f'{keyname} found in crypt: {given_key}')
            return found_key

        # self.log(f'{keyname} not found!!')
            

    def getkey(self, keyname, keychain={}, uri=None):
        # cached?
        # if hasattr(self,'_'+keyname) and getattr(self,'_'+keyname):
            # return getattr(self,'_'+keyname)
        if keyname in self._keychain: return self._keychain[keyname]

        # self.log(f'keyname={keyname}, keychain={keychain.keys()}, uri={uri}')

        # 1) I already have this key stored in either the keychain or the crypt; return straight away
        key = self.findkey(keyname, keychain, uri)
        if key:
            # self.log(f'>> I have {key} already, returning')
            return key

        ## 2) I can assemble the key
        # self.log(f'assembling key: {keyname}_encr + {keyname}_decr')
        key_encr = self.findkey(keyname+'_encr', keychain,uri)
        key_decr = self.findkey(keyname+'_decr', keychain, uri)
        key = self.assemble_key(key_encr, key_decr, keyname+'_encr', keyname+'_decr')
        return key

    def get_cell(self, str_or_key_or_cell):
        # self.log('getting decr cell for',str_or_key_or_cell)

        if type(str_or_key_or_cell)==SCellSeal:
            return str_or_key_or_cell
        elif type(str_or_key_or_cell)==str:
            return SCellSeal(passphrase=str_or_key_or_cell)
        elif type(str_or_key_or_cell)==bytes:
            return SCellSeal(key=str_or_key_or_cell)

    def assemble_key(self, key_encr, key_decr, key_encr_name=None, key_decr_name=None):
        # self.log(f'assembling key: {key_decr} decrypting {key_encr}')

        # need the encrypted half
        if not key_encr:
            # self.log('!! encrypted half not given')
            return
        if not key_decr:
            if self.passphrase:
                key_decr = self.passphrase
            else:
                # self.log('!! decryptor half not given')
                return

        # need some way to regenerate the decryptor
        decr_cell = self.get_cell(key_decr)

        # need the decryptor half
        if not decr_cell:
            # self.log('!! decryptor cell not regenerable')
            return

        # decrypt!
        try:
            self.log(f'>> decrypting {key_encr_name} with {key_decr_name}\n({key_encr} with cell {decr_cell}')
            key = decr_cell.decrypt(key_encr)
            # self.log('assembled_key built:',key)
            return key
        except ThemisError as e:
            self.log('!! decryption failed:',e)
            return

    # Concrete keys
    ## (1) Final keys
    def pubkey(self, force=False, **kwargs):
        # if force or not hasattr(self,'_pubkey') or not self._pubkey:
        #     self._pubkey = self.getkey(keyname='pubkey',uri=self.name,**kwargs)
        # return self._pubkey
        
        x=self.getkey(keyname='pubkey',uri=self.name,**kwargs)
        print('weee',x)
        return x

    def privkey(self, force=False, **kwargs):
        # if force or not hasattr(self,'_privkey') or not self._privkey:
            # self._privkey=self.getkey(keyname='privkey',uri=self.pubkey(**kwargs),**kwargs)
        # return self._privkey
        return self.getkey(keyname='privkey',uri=self.pubkey(**kwargs),**kwargs)

    def adminkey(self, force=False, **kwargs):
        # if force or not hasattr(self,'_adminkey') or not self._adminkey:
            # self._adminkey=self.getkey(keyname='adminkey',uri=self.privkey(**kwargs),**kwargs)
        # return self._adminkey
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

    def gen_encr_keys(self,keychain,keys_to_gen,passphrase=None):
        # generate encrypted keys too
        for key_name in keys_to_gen:
            if key_name.endswith('_encr') and key_name not in keychain:
                # encrypt it with the associated decr
                self.log(f'let\'s encrypt {key_name}!')
                name_of_what_to_encrypt = key_name[:-len('_encr')]
                the_key_to_encrypt_it_with = name_of_what_to_encrypt + '_decr'
                if the_key_to_encrypt_it_with in keychain and name_of_what_to_encrypt in keychain:
                    _key_decr = keychain[the_key_to_encrypt_it_with]
                    _key = keychain[name_of_what_to_encrypt]
                    self.log(f'about to encrypt key {name_of_what_to_encrypt}, using {the_key_to_encrypt_it_with}, which is a type {KEYMAKER_DEFAULT_KEY_TYPES[the_key_to_encrypt_it_with]} and has value {keychain[the_key_to_encrypt_it_with]}')
                    _key_encr = _key_decr.encrypt(_key)
                    # self.log(f'{_key}\n-- encrypting ----->\n{_key_encr}')
                    keychain[key_name]=_key_encr
        return keychain



    def forge_new_keys(self,
                        name=None,
                        passphrase=None,
                        keys_to_save = KEYMAKER_DEFAULT_KEYS_TO_SAVE,
                        keys_to_return = KEYMAKER_DEFAULT_KEYS_TO_RETURN,
                        keys_to_gen = KEYMAKER_DEFAULT_KEYS_TO_GEN,
                        key_types = KEYMAKER_DEFAULT_KEY_TYPES):
        self.log('forging new keys...',name,self.name)
        self.log('keys_to_save:',keys_to_save)
        self.log('keys_to_return',keys_to_return)
        


        if not name: name=self.name

        keys_to_gen = set(keys_to_gen) | set(keys_to_save) | set(keys_to_return)
        keys_to_gen = sorted(list(keys_to_gen),key=lambda x: x.count('_'))
        self.log('keys_to_gen =',keys_to_gen)
        key_types = dict([(k,key_types[k]) for k in keys_to_gen])
        self.log('key_types =',key_types)

        # get decryptor keys!
        keychain = self.gen_keys_from_types(key_types,passphrase=passphrase)
        self.log('keychain 1 =',keychain)
        
        # gen encrypted keys!
        keychain = self.gen_encr_keys(keychain,keys_to_gen,passphrase=passphrase)
        self.log('keychain 2 =',keychain)

        # save keys!
        keys_saved = self.save_keychain(name,keychain,keys_to_save)
        self.log('keys_saved =',keys_saved)

        # return keys!
        keys_returned = self.return_keychain(keychain,keys_to_return)
        return keys_returned
        
                
    def return_keychain(self,keychain,keys_to_return):
        keychain_toreturn = {}
        for key in keys_to_return:
            if key in keychain:
                keychain_toreturn[key]=keychain[key]
        return keychain_toreturn


    def save_keychain(self,name,keychain,keys_to_save):
        keys_saved = []

        # filter for transfer
        for k,v in keychain.items():
            if issubclass(type(v),KomradeKey):
                v=v.data
            keychain[k]=v

        # for k,v in keychain_tosave.items():        
        if 'pubkey' in keys_to_save or 'privkey' in keys_to_save or 'adminkey' in keys_to_save:
            # unless we're the operator or the telephone
            if not self.name in {OPERATOR_NAME,TELEPHONE_NAME}:
                raise KomradeException('there is no private property in a socialist network! all keys must be split between komrades')
            else:
                if 'pubkey' in keys_to_save and 'pubkey' in keychain:
                    keys_saved+=['pubkey']
                    self.crypt_keys.set(name,keychain['pubkey'],prefix='/pubkey/')
                    
                if 'privkey' in keys_to_save and 'privkey' in keychain:
                    keys_saved+=['privkey']
                    self.crypt_keys.set(keychain['pubkey'],keychain['privkey'],prefix='/privkey/')
                
                if 'adminkey' in keys_to_save and 'adminkey' in keychain:
                    keys_saved+=['adminkey']
                    self.crypt_keys.set(keychain['privkey'],keychain['adminkey'],prefix='/adminkey/')
                

        ### SAVE ENCRYPTED KEYS?        
        if 'pubkey_encr' in keys_to_save and 'pubkey_encr' in keychain:
            keys_saved+=['pubkey_encr']
            self.crypt_keys.set(name,keychain['pubkey_encr'],prefix='/pubkey_encr/')
        
        if 'privkey_encr' in keys_to_save and 'privkey_encr' in keychain:
            keys_saved+=['privkey_encr']
            self.crypt_keys.set(keychain['pubkey'],keychain['privkey_encr'],prefix='/privkey_encr/')
        
        if 'adminkey_encr' in keys_to_save and 'adminkey_encr' in keychain:
            keys_saved+=['adminkey_encr']
            self.crypt_keys.set(keychain['privkey'],keychain['adminkey_encr'],prefix='/adminkey_encr/')
        # stop

        # save decrypted keys?
        if 'pubkey_decr' in keys_to_save and 'pubkey_decr' in keychain:
            keys_saved+=['pubkey_decr']
            self.crypt_keys.set(name,keychain['pubkey_decr'],prefix='/pubkey_decr/')
        
        if 'privkey_decr' in keys_to_save and 'privkey_decr' in keychain:
            keys_saved+=['privkey_decr']
            self.crypt_keys.set(keychain['pubkey'],keychain['privkey_decr'],prefix='/privkey_decr/')
        
        if 'adminkey_decr' in keys_to_save and 'adminkey_decr' in keychain:
            keys_saved+=['adminkey_decr']
            self.crypt_keys.set(keychain['privkey'],keychain['adminkey_decr'],prefix='/adminkey_decr/')
        
        if 'pubkey_encr_encr' in keys_to_save and 'pubkey_encr_encr' in keychain:
            keys_saved+=['pubkey_encr_encr']
            self.crypt_keys.set(name,keychain['pubkey_decr_encr'],prefix='/pubkey_decr_encr/')
        
        if 'privkey_encr_encr' in keys_to_save and 'privkey_encr_encr' in keychain:
            keys_saved+=['privkey_encr_encr']    
            self.crypt_keys.set(keychain['pubkey_decr'],keychain['privkey_decr_encr'],prefix='/privkey_decr_encr/')
        
        if 'adminkey_encr_encr' in keys_to_save and 'adminkey_encr_encr' in keychain:
            keys_saved+=['adminkey_encr_encr']
            self.crypt_keys.set(keychain['privkey_decr'],keychain['adminkey_decr_encr'],prefix='/adminkey_decr_encr/')

        if 'pubkey_decr_encr' in keys_to_save and 'pubkey_decr_encr' in keychain:
            keys_saved+=['pubkey_decr_encr']
            self.crypt_keys.set(name,keychain['pubkey_decr_encr'],prefix='/pubkey_decr_encr/')
        
        if 'privkey_decr_encr' in keys_to_save and 'privkey_decr_encr' in keychain:
            keys_saved+=['privkey_decr_encr']
            self.crypt_keys.set(keychain['pubkey_decr'],keychain['privkey_decr_encr'],prefix='/privkey_decr_encr/')
        
        if 'adminkey_decr_encr' in keys_to_save and 'adminkey_decr_encr' in keychain:
            keys_saved+=['adminkey_decr_encr']
            self.crypt_keys.set(keychain['privkey_decr'],keychain['adminkey_decr_encr'],prefix='/adminkey_decr_encr/')
        
        if 'pubkey_decr_decr' in keys_to_save and 'pubkey_decr_decr' in keychain:
            keys_saved+=['pubkey_decr_decr']
            self.crypt_keys.set(name,keychain['pubkey_decr_decr'],prefix='/pubkey_decr_decr/')
        
        if 'privkey_decr_decr' in keys_to_save and 'privkey_decr_decr' in keychain:
            keys_saved+=['privkey_encr_encr']
            self.crypt_keys.set(keychain['pubkey_decr'],keychain['privkey_decr_decr'],prefix='/privkey_decr_decr/')
        
        if 'adminkey_decr_decr' in keys_to_save and 'adminkey_decr_decr' in keychain:
            keys_saved+=['adminkey_decr_decr']
            self.crypt_keys.set(keychain['privkey_decr'],keychain['adminkey_decr_decr'],prefix='/adminkey_decr_decr/')
        
        if 'pubkey_decr_decr' in keys_to_save and 'pubkey_decr_decr' in keychain:
            keys_saved+=['pubkey_decr_decr']
            self.crypt_keys.set(name,keychain['pubkey_decr_decr'],prefix='/pubkey_decr_decr/')
        
        if 'privkey_decr_decr' in keys_to_save and 'privkey_decr_decr' in keychain:
            keys_saved+=['privkey_encr_encr']
            self.crypt_keys.set(keychain['pubkey_decr'],keychain['privkey_decr_decr'],prefix='/privkey_decr_decr/')
        
        if 'adminkey_decr_decr' in keys_to_save and 'adminkey_decr_decr' in keychain:
            keys_saved+=['adminkey_decr_decr']
            self.crypt_keys.set(keychain['privkey_decr'],keychain['adminkey_decr_decr'],prefix='/adminkey_decr_decr/')

        # return in dict form
        keys_saved_d = {}
        for key_saved in keys_saved:
            if key_saved in keychain:
                keys_saved_d[key_saved] = keychain[key_saved]
        return keys_saved_d


    def valid_keychain(self,keychain_b64_d):
        valid_kc = {}

        for k,v in keychain_b64_d.items():
            self.log('incoming <--',k,v)
            if type(v)==bytes: 
                data = v
            elif type(v)==str:
                if not isBase64(v):
                    self.log('not valid input!')
                    continue
                
                # first try to get from string to bytes
                try:
                    data = v.encode()
                    self.log('data',data)
                except UnicodeEncodeError:
                    self.log('not valid unicode?')
                    continue
            
            # then try to get from b64 bytes to raw bytes
            if isBase64(data):
                valid_kc[k]=b64decode(data)
            else:
                valid_kc[k]=data
        
        return valid_kc

    def assemble(self,_keychain):
        # last minute assemblies?
        encr_keys = [k for k in _keychain if k.endswith('_encr')]
        for ekey in encr_keys:
            eval=_keychain[ekey]
            if not eval: continue

            unencrkey = ekey[:-len('_encr')]
            if unencrkey in _keychain: continue
            
            decrkey = unencrkey+'_decr'
            if decrkey not in _keychain: continue
            
            dval=_keychain[decrkey]
            if not dval: continue

            self.log(ekey,decrkey,'??')
            self.log(eval,dval,'????')
            
            new_val = self.assemble_key(eval,dval)
            self.log('!!#!',new_val)
            if new_val:
                _keychain[unencrkey] = new_val
        return _keychain


    def keychain(self,passphrase=None,force=False,allow_builtin=True,extra_keys={},keys_to_gen=KEYMAKER_DEFAULT_KEYS_TO_GEN,**kwargs):
        # assemble as many keys as we can!
        # if not force and hasattr(self,'_keychain') and self._keychain: return self._keychain
        if passphrase: self.passphrase=passphrase
        _keychain = {**extra_keys, **self._keychain}
        self.log('_keychain at start of keychain() =',_keychain)
        for keyname in keys_to_gen+keys_to_gen:
            # if keyname in _keychain and _keychain[keyname]: continue
            # self.log('??',keyname,keyname in self._keychain,'...')
            if hasattr(self,keyname):
                method=getattr(self,keyname)
                res=method(keychain=_keychain, **kwargs)
                # self.log('res <--',res)
                if res:
                    _keychain[keyname]=res
        
        
        _keychain = self.assemble(_keychain)
        _keychain = self.assemble(_keychain)
        self._keychain = _keychain
        return _keychain

        



        return _keychain
        


if __name__ == '__main__':
    keymaker = Keymaker('marx69')
    keychain = keymaker.forge_new_keys()

    print(keychain)