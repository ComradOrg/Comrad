"""
Storage for both keys and data
"""
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from simplekv.fs import FilesystemStore
from simplekv.memory.redisstore import RedisStore
import redis
import hashlib,os
import zlib
from pythemis.exception import ThemisError



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
                from komrade.backend.keymaker import make_key_discreet
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
            from komrade.backend.keymaker import KomradeSymmetricKeyWithPassphrase
            self.key = KomradeSymmetricKeyWithPassphrase(
                passphrase=self.secret
            )
            encryptor_func = self.key.encrypt
            decryptor_func = self.key.decrypt
        self.encryptor_func=encryptor_func
        self.decryptor_func=decryptor_func
        
        #self.store = FilesystemStore(self.fn)
        self.store = RedisStore(redis.StrictRedis())


    def log(self,*x):
        if LOG_GET_SET:
            super().log(*x)
        
    def hash(self,binary_data):
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
        return bool(self.get(k,prefix=prefix))


    def set(self,k,v,prefix='',override=False,encrypt=True):
        if self.has(k,prefix=prefix) and not override:
            self.log(f"I'm afraid I can't let you do that, overwrite someone's data!\n\nat {prefix}{k} = {v}")
            return False #(False,None,None)
        
        k_b=self.package_key(k,prefix=prefix)
        k_b_hash = self.hash(k_b)
        v_b=self.package_val(v,encrypt = (self.encrypt_values and encrypt))
        if not override:
            self.log(f'''Crypt.set(\n\t{k_b}\n\n\t{k_b_hash}\n\n\t{v_b}\n)''')
        self.store.put(k_b_hash,v_b)
        return True

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
        r=self.store.delete(k_b_hash)
        return r
        

    def get(self,k,prefix=''):
        k_b=self.package_key(k,prefix=prefix)
        k_b_hash = self.hash(k_b)
        try:
            v=self.store.get(k_b_hash)
        except KeyError:
            return None
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
        self.keyname=keyname
        self.prefix=prefix
        self.encryptor_func=encryptor_func
        self.decryptor_func=decryptor_func

    def __repr__(self):
        return f"""
(CryptList)
val_b_encr = {self.val_b_encr}
val_b = {self.val_b}
values = {self.values}
        """
    
    @property
    def val_b_encr(self):
        res = self.crypt.get(
            self.keyname,
            prefix=self.prefix
        )
        self.log('res from crypt:',res)
        return res
    
    @property
    def val_b(self):
        val_b_encr=self.val_b_encr
        if not val_b_encr: return None
        return self.decryptor_func(val_b_encr)
    
    @property
    def values(self):
        if not hasattr(self,'_values') or not self._values:    
            val_b=self.val_b
            if not val_b: return []
            self._values = pickle.loads(val_b)
        return self._values

    def prepend(self,x_l):
        return self.append(x_l,insert=0)

    def append(self,x_l,insert=None):
        if type(x_l)!=list: x_l=[x_l]
        val_l = self.values
        self.log('val_l =',val_l)
        x_l = [x for x in x_l if not x in set(val_l)]
        # print('val_l =',val_l)
        for x in x_l:
            if insert is not None:
                val_l.insert(insert,x)
            else:
                val_l.append(x)
            # print('val_l2 =',val_l)
        return self.set(val_l)

    def set(self,val_l):
        self._values = val_l

        val_b = pickle.dumps(val_l)
        val_b_encr = self.encryptor_func(val_b)
        return self.crypt.set(
            self.keyname,
            val_b_encr,
            prefix=self.prefix,
            override=True
        )

    def remove(self,l):
        if type(l)!=list: l=[l]
        lset=set(l)
        values = [x for x in self.values if x not in lset]
        return self.set(values)







class CryptListRedis(Logger):
    def __init__(self,keyname,prefix='',**y):
        self.redis = redis.StrictRedis()
        # self.store = RedisStore(self.redis)
        self.keyname=b64enc_s(prefix)+b64enc_s(keyname)
        self.log('loading CryptList',keyname,prefix,self.keyname)

    def package_val(self,val):
        if type(val)==bytes: val=val.decode()
        # return b64enc_s(val)
        return val

    def unpackage_val(self,val):
        if type(val)==str: val=val.encode()
        # return b64dec(val)
        return val

    def append(self,val):
        self.log('<--val',val)
        if type(val)==list: return [self.append(x) for x in val]
        val_x = self.package_val(val)
        res = self.redis.rpush(self.keyname,val_x)
        self.log('-->',res)
        return res

    def prepend(self,val):
        self.log('<--val',val)
        if type(val)==list: return [self.prepend(x) for x in val]
        val_x = self.package_val(val)
        res = self.redis.lpush(self.keyname,val_x)
        self.log('-->',res)
        return res

    @property
    def values(self):    
        l = self.redis.lrange(self.keyname, 0, -1 )
        vals = [self.unpackage_val(x) for x in l]
        self.log('-->',vals)
        return vals

    def remove(self,val):
        self.log('<--',val)
        if type(val)==list: return [self.remove(x) for x in val]
        val_x = self.package_val(val)
        res = self.redis.lrem(self.keyname, 0, val_x)
        self.log('-->',res)
        return res



if __name__=='__main__':
    crypt = Crypt('testt')

    from komrade import KomradeSymmetricKeyWithPassphrase
    key = KomradeSymmetricKeyWithPassphrase()


    crypt_list = CryptList(
        keyname='MyInbox2',
    )

    print(crypt_list.values)

    # print(crypt_list.remove('cool thing 0'))

    # print(crypt_list.append('cool thing 1'))
    
    print(crypt_list.append('#1 baby'))
    print(crypt_list.append('cool thing 0'))
    print(crypt_list.prepend('#0 baby'))

    print(crypt_list.remove('cool thing 0'))

    print(crypt_list.values)