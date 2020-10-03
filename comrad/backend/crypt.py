"""
Storage for both keys and data
"""
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from comrad import *
# from simplekv.fs import FilesystemStore
# from simplekv.memory.redisstore import RedisStore
# import redis
import hashlib,os
import zlib
from pythemis.exception import ThemisError
# from vedis import Vedis
# from walrus.tusks.rlite import WalrusLite
import hirlite

LOG_GET_SET = 0





class Crypt(Logger):
    def __init__(self,
            name=None,
            fn=None,
            use_secret=CRYPT_USE_SECRET,
            path_secret=PATH_CRYPT_SECRET,
            encrypt_values=False,
            encryptor_func=None,
            decryptor_func=None):
        
        # defaults
        if not name and fn: name=os.path.basename(fn).replace('.','_')
        self.name,self.fn=name,fn

        
        # use secret? for salting
        if use_secret and path_secret:
            if not os.path.exists(path_secret):
                self.secret = get_random_binary_id()
                from comrad.backend.keymaker import make_key_discreet
                self.log('shhh! creating secret:',make_key_discreet(self.secret))
                with open(path_secret,'wb') as of:
                    of.write(self.secret)
            else:
                with open(path_secret,'rb') as f:
                    self.secret = f.read()
        else:
            self.secret = b''
        self.encrypt_values = encrypt_values
        if self.secret and encrypt_values and (not encryptor_func or not decryptor_func):
            from comrad.backend.keymaker import ComradSymmetricKeyWithPassphrase
            self.key = ComradSymmetricKeyWithPassphrase(
                passphrase=self.secret
            )
            encryptor_func = self.key.encrypt
            decryptor_func = self.key.decrypt
        self.encryptor_func=encryptor_func
        self.decryptor_func=decryptor_func
        
        # self.store = FilesystemStore(self.fn)
        # self.store = RedisStore(redis.StrictRedis())
        # self.db = Vedis(self.fn)
        # self.db = WalrusLite(self.fn)
        self.db = hirlite.Rlite(path=self.fn)


    def log(self,*x,**y):
        if LOG_GET_SET:
            super().log(*x)
        
    def hash(self,binary_data):
        # return binary_data
        return hasher(binary_data,self.secret)

    def force_binary(self,k_b):
        if k_b is None: return None
        if type(k_b)==str: k_b=k_b.encode()
        if type(k_b)!=bytes: k_b=k_b.decode()
        return k_b

    def package_key(self,k,prefix=''):
        if not k: return b''
        
        k_b = self.force_binary(k)
        k_b2 = self.force_binary(prefix) + k_b
        return k_b2

    def package_val(self,k,encrypt=None):
        if encrypt is None: encrypt=self.encrypt_values
        k_b = self.force_binary(k)
        if encrypt:
            try:
                k_b = self.encryptor_func(k_b)
            except ThemisError as e:
                self.log('!! ENCRYPTION ERROR:',e)
        return k_b

    def unpackage_val(self,k_b,encrypt=None):
        if encrypt is None: encrypt=self.encrypt_values
        if encrypt:
            try:
                k_b = self.decryptor_func(k_b)
            except ThemisError as e:
                self.log('!! DECRYPTION ERROR:',e)
        return k_b

    def has(self,k,prefix=''):
        got=self.get(k,prefix=prefix)
        # self.log('has got',got)
        return bool(got)


    def set(self,k,v,prefix='',override=False,encrypt=True):
        if self.has(k,prefix=prefix) and not override:
            self.log(f"I'm afraid I can't let you do that, overwrite someone's data!\n\nat {prefix}{k} = {v}")
            return False #(False,None,None)
        
        k_b=self.package_key(k,prefix=prefix)
        k_b_hash = self.hash(k_b)
        v_b=self.package_val(v,encrypt = (self.encrypt_values and encrypt))
        if not override:
            self.log(f'''Crypt.set(\n\t{k_b}\n\n\t{k_b_hash}\n\n\t{v_b}\n)''')
        
        #self.store.put(k_b_hash,v_b)
        #with self.db.transaction():
            # self.db[k_b_hash]=v_b
        return self.db.command('set',k_b_hash,v_b)
        # return True

    def exists(self,k,prefix=''):
        return self.has(k,prefix=prefix)

    def key2hash(self,k,prefix=''):
        return self.hash(
            self.package_key(
                prefix + k
            )
        )

    def delete(self,k,prefix=''):
        k_b=self.package_key(k,prefix=prefix)
        k_b_hash = self.hash(k_b)

        v = self.db.command('del',k_b_hash)
        self.log('<--',v)
        
        return v
        

    def get(self,k,prefix=''):
        k_b=self.package_key(k,prefix=prefix)
        k_b_hash = self.hash(k_b)
        # v=self.db.get(k_b_hash)
        self.log('getting k',k,'with prefix',prefix)
        self.log('getting k_b',k_b)
        self.log('getting k_b_hash',k_b_hash)
        
        v = self.db.command('get',k_b_hash)
        self.log('<--',v)

        v_b=self.unpackage_val(v)
        return v_b


class KeyCrypt(Crypt):
    def __init__(self):
        return super().__init__(name=PATH_CRYPT_CA_KEYS.replace('.','_'))


class DataCrypt(Crypt):
    def __init__(self):
        return super().__init__(name=PATH_CRYPT_CA_DATA.replace('.','_'))



class CryptList(Crypt):  # like inbox
    def __init__(self,
            crypt,
            keyname,
            prefix='',
            encryptor_func=lambda x: x,
            decryptor_func=lambda x: x):
        
        self.crypt=crypt
        self.db=self.crypt.db
        self.keyname=self.crypt.package_key(keyname,prefix)

    @property
    def values(self): return list(self.l)

    def package_val(self,val):
        # if type(val)!=bytes: val=val.encode()
        return val

    def unpackage_val(self,val):
        # if type(val)==str: val=val.encode()
        return val

    def append(self,val):
        self.log('<--val',val)
        if type(val)==list: return [self.append(x) for x in val]
        val_x = self.package_val(val)
        # with self.db.transaction():
            # res = self.db.lpush(self.keyname,val_x)
        res = self.db.command('rpush',self.keyname,val_x)
        self.log('-->',res)
        return res

    def prepend(self,val):
        self.log('<--val',val)
        if type(val)==list: return [self.prepend(x) for x in val]
        val_x = self.package_val(val)
        res = self.db.command('lpush',self.keyname,val_x)
        self.log('-->',res)
        return res

    @property
    def values(self):
        l = self.db.command('lrange',self.keyname, '0', '-1')
        self.log('<-- l',l)
        if not l: return []
        vals = [self.unpackage_val(x) for x in l]
        self.log('-->',vals)
        return vals

    def remove(self,val):
        self.log('<--',val)
        if type(val)==list: return [self.remove(x) for x in val]
        val_x = self.package_val(val)
        self.db.command('lrem',self.keyname,'0',val_x)




if __name__=='__main__':
    crypt = Crypt(fn='tes22t.db')
    print(crypt.set(
        'testing22',
        b'wooooooboy',
        prefix='/test/',
    ))

    print('got back', crypt.get(
        'testing22',
        prefix='/test/'
    ))



    crypt_list = CryptList(
        keyname='MyInbosdx35',
        crypt=crypt
    )

    print(crypt_list.values)

    # print(crypt_list.remove('cool thing 0'))

    # print(crypt_list.append('cool thing 1'))
    
    print(crypt_list.append('Appended'))
    print(crypt_list.append('cool thing 0'))
    print(crypt_list.prepend('Prepended'))
    print()
    print()
    print(crypt_list.remove('cool thing 0'))
    print()
    print()
    print(crypt_list.values)