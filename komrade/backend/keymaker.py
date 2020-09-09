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
    def __init__(self,passphrase=DEBUG_DEFAULT_PASSPHRASE, why=WHY_MSG):
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
    def __init__(self,
                name=None,
                passphrase=DEBUG_DEFAULT_PASSPHRASE,
                uri_id=None,
                keychain={},
                path_crypt_keys=None,
                path_crypt_data=None):
        
        # set defaults
        self.name=name
        self._uri_id=uri_id
        self._pubkey=None
        self._keychain=keychain
        self.passphrase=passphrase
        self.path_crypt_keys=path_crypt_keys
        self.path_crypt_data=path_crypt_data


    def find_pubkey(self):
        global TELEPHONE_KEYCHAIN,OPERATOR_KEYCHAIN
        #self.log('keychain?',self.keychain())
        if 'pubkey' in self._keychain and self._keychain['pubkey']:
            return self._keychain['pubkey']
        
        res = self.crypt_keys.get(self.name, prefix='/pubkey/')
        if res: return res
        
        res = self.load_qr(self.name)
        if res: return res

        self.log('I don\'t know my public key!')
        raise KomradeException(f'I don\'t know my public key!\n{self}\n{self._keychain}')
        #return None

        

    def keychain(self,look_for=KEYMAKER_DEFAULT_ALL_KEY_NAMES):
        # load existing keychain
        keys = self._keychain #self._keychain = keys = {**self._keychain}
        
        # make sure we have the pubkey
        if not 'pubkey' in self._keychain: self._keychain['pubkey']=self.find_pubkey()
        pubkey=self._keychain['pubkey']

        # get uri
        uri = b64encode(pubkey)

        # get from cache
        for keyname in look_for:
            if keyname in keys and keys[keyname]: continue
            key = self.crypt_keys.get(uri,prefix=f'/{keyname}/')
            if key: keys[keyname]=key
        
        # try to assemble
        keys = self.assemble(self.assemble(keys))
        
        #store to existing set
        self._keychain = keys
        
        #return
        return keys

    @property
    def pubkey(self): return self.keychain().get('pubkey')
    @property
    def privkey(self): return self.keychain().get('privkey')
    @property
    def adminkey(self): return self.keychain().get('adminkey')



    def load_qr(self,name):
        # try to load?
        contact_fnfn = os.path.join(PATH_QRCODES,name+'.png')
        print(contact_fnfn,os.path.exists(contact_fnfn))
        if not os.path.exists(contact_fnfn): return ''
        # with open(contact_fnfn,'rb') as f: dat=f.read()
        from pyzbar.pyzbar import decode
        from PIL import Image
        res= decode(Image.open(contact_fnfn))[0].data

        # self.log('QR??',res,b64decode(res))
        return b64decode(res)

    @property
    def uri_id(self):
        if not self._uri_id:
            pubkey = self.find_pubkey()
            self._uri_id = b64encode(pubkey)
        return self._uri_id


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

    def exists(self):
        return self.crypt_keys.exists(self.name,prefix='/pubkey_encr/') or self.crypt_keys.exists(self.name,prefix='/pubkey_decr/') or self.crypt_keys.exists(self.name,prefix='/pubkey/')

    ### CREATING KEYS
    
    def get_new_keys(self):
        raise KomradeException('Every keymaker must make their own get_new_keys() !')




    def gen_keys_from_types(self,key_types=KEYMAKER_DEFAULT_KEY_TYPES,passphrase=DEBUG_DEFAULT_PASSPHRASE):
        """
        Get new asymmetric/symmetric keys, given a dictionary of constants describing their type
        """

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



    def gen_encr_keys(self,keychain,keys_to_gen,passphrase=DEBUG_DEFAULT_PASSPHRASE):
        """
        Encrypt other keys with still other keys!
        """
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
                        passphrase=DEBUG_DEFAULT_PASSPHRASE,
                        keys_to_save = KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_SERVER,
                        keys_to_return = KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_CLIENT,
                        keys_to_gen = KEYMAKER_DEFAULT_KEYS_TO_GEN,
                        key_types = KEYMAKER_DEFAULT_KEY_TYPES):
        self.log('forging new keys...',name,self.name)
        self.log('keys_to_save:',keys_to_save)
        self.log('keys_to_return',keys_to_return)
        
        # name
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
        # get URI id to save under (except for pubkeys, accessible by name)
        uri_id,keys_saved,keychain = self.save_keychain(name,keychain,keys_to_save)
        self.log('uri_id =',uri_id)
        self.log('keys_saved =',keys_saved)
        self.log('keychain =',keychain)

        # return keys!
        keys_returned = self.return_keychain(keychain,keys_to_return)
        return {'uri_id':uri_id,'_keychain':keys_returned}
        
                
    def return_keychain(self,keychain,keys_to_return=None):
        keychain_toreturn = {}
        if not keys_to_return: keys_to_return = list(keychain.keys())
        for key in keys_to_return:
            if key in keychain:
                keychain_toreturn[key]=keychain[key]
        return keychain_toreturn

    def save_uri_as_qrcode(self,name=None,uri_id=None,odir=None):
        if not uri_id: uri_id = get_random_id() + get_random_id()
        uri_id = self.uri_id
        if not uri_id and not self.uri_id: raise KomradeException('Need URI id to save!')

        # gen
        import pyqrcode
        qr = pyqrcode.create(uri_id)
        if not odir: odir = PATH_QRCODES
        ofnfn = os.path.join(odir,self.name+'.png')
        qr.png(ofnfn,scale=5)
        self.log('>> saved:',ofnfn)

    def save_keychain(self,name,keychain,keys_to_save=None,uri_id=None):
        if not keys_to_save: keys_to_save = list(keychain.keys())
        if not uri_id: uri_id = b64encode(keychain['pubkey'].data).decode() #uri_id = get_random_id() + get_random_id()
        self.log(f'SAVING KEYCHAIN FOR {name} under URI {uri_id}')
        self._uri_id = uri_id
        # filter for transfer
        for k,v in keychain.items():
            if issubclass(type(v),KomradeKey):
                v=v.data
            keychain[k]=v
        
        # save keychain
        keys_saved_d={}
        for keyname in keys_to_save:
            if not '_' in keyname and keyname!='pubkey':
                raise KomradeException('there is no private property in a socialist network! all keys must be split between komrades')
            if keyname in keychain:
                # uri = uri_id
                uri = uri_id if name!='pubkey' else name
                self.crypt_keys.set(uri,keychain[keyname],prefix=f'/{keyname}/')
                keys_saved_d[keyname] = keychain[keyname]

        # save pubkey as QR
        if not 'pubkey' in keys_saved_d:
            self.log('did not save pubkey in crypt, storing as QR...')
            self.save_uri_as_qrcode(name=name, uri_id=uri_id, odir=PATH_QRCODES)

        return (uri_id,keys_saved_d,keychain)

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

            # self.log(ekey,decrkey,'??')
            # self.log(eval,dval,'????')
            
            new_val = self.assemble_key(eval,dval)
            # self.log('!!#!',new_val)
            if new_val:
                _keychain[unencrkey] = new_val
        return _keychain

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
            # self.log(f'>> decrypting {key_encr_name} with {key_decr_name}\n({key_encr} with cell {decr_cell}')
            key = decr_cell.decrypt(key_encr)
            # self.log('assembled_key built:',key)
            return key
        except ThemisError as e:
            # self.log('!! decryption failed:',e)
            return

    def get_cell(self, str_or_key_or_cell):
        # self.log('getting decr cell for',str_or_key_or_cell)

        if type(str_or_key_or_cell)==SCellSeal:
            return str_or_key_or_cell
        elif type(str_or_key_or_cell)==str:
            return SCellSeal(passphrase=str_or_key_or_cell)
        elif type(str_or_key_or_cell)==bytes:
            return SCellSeal(key=str_or_key_or_cell)


    # def keychain(self,
    #             passphrase=DEBUG_DEFAULT_PASSPHRASE,
    #             extra_keys={},
    #             keys_to_gen=KEYMAKER_DEFAULT_KEYS_TO_GEN,
    #             uri_id=None,
    #             **kwargs):

    #     # assemble as many keys as we can!
    #     self.log(f'''keychain(
    #         passphrase={passphrase},
    #         extra_keys={extra_keys},
    #         keys_to_gen={keys_to_gen},
    #         uri_id={uri_id},
    #         **kwargs = {kwargs}
    #     )''')

    #     if not uri_id: uri_id = self.uri_id
    #     if not uri_id and not self.uri_id: 
    #         raise KomradeException('Need URI id to complete finding of keys!')
    #     self.log('getting keychain for uri ID:',uri_id)

    #     # if not force and hasattr(self,'_keychain') and self._keychain: return self._keychain
    #     if passphrase: self.passphrase=passphrase

    #     # start off keychain
    #     _keychain = {**extra_keys, **self._keychain}
    #     self.log('_keychain at start of keychain() =',_keychain)
        
    #     # find
    #     for keyname in keys_to_gen:
    #         if keyname in _keychain and _keychain[keyname]: continue
    #         # self.log('??',keyname,keyname in self._keychain,'...')
    #         newkey = self.crypt_keys.get(uri_id,prefix=f'/{keyname}/')
    #         if newkey: _keychain[keyname] = newkey
        
    #     # return
    #     _keychain = self.assemble(_keychain)
    #     self._keychain = _keychain
    #     return _keychain

        



        return _keychain
        


if __name__ == '__main__':
    keymaker = Keymaker('marx69')
    keychain = keymaker.forge_new_keys()

    print(keychain)