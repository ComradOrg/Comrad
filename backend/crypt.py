"""
Storage for both keys and data
"""
from simplekv.fs import FilesystemStore
from simplekv.memory.redisstore import RedisStore
import redis
import hashlib,os
from pythemis.skeygen import KEY_PAIR_TYPE, GenerateKeyPair
from pythemis.smessage import SMessage, ssign, sverify
from pythemis.skeygen import GenerateSymmetricKey
from pythemis.scell import SCellSeal
from pythemis.exception import ThemisError
import zlib





class Crypt(object):
    def log(self,*x): print(*x)

    def __init__(self,name=None,fn=None,cell=None):
        if not name and fn: name=os.path.basename(fn).replace('.','_')

        self.name,self.fn,self.cell = name,fn,cell
        self.store = FilesystemStore(self.fn)
        
    def hash(self,binary_data):
        return hashlib.sha256(binary_data).hexdigest()
        # return zlib.adler32(binary_data)

    def force_binary(self,k_b):
        if type(k_b)==str: k_b=k_b.encode()
        if type(k_b)!=bytes: k_b=str(k_b).encode()
        return k_b

    def package_key(self,k):
        k_b = self.force_binary(k)
        # k_b = self.cell.encrypt(k_b)
        k_b = self.hash(k_b)
        return k_b

    def package_val(self,k):
        k_b = self.force_binary(k)
        k_b = self.cell.encrypt(k_b)
        return k_b


    def unpackage_val(self,k_b):
        try:
            return self.cell.decrypt(k_b)
        except ThemisError:
            return None


    def set(self,k,v):
        self.log('set() k -->',k)
        k_b=self.package_key(k)
        self.log('set() k_b -->',k_b)

        self.log('set() v -->',v)
        v_b=self.package_val(v)
        self.log('set() v_b -->',v_b)
        
        return self.store.put(k_b,v_b)

    def get(self,k):
        self.log('get() k -->',k)
        k_b=self.package_key(k)
        self.log('get() k_b -->',k_b)

        v=self.store.get(k_b)
        self.log('get() v -->',v)
        v_b=self.unpackage_val(v)
        self.log('get() v_b -->',v_b)
        return v_b


class KeyCrypt(Crypt):
    def __init__(self):
        return super().__init__(name=PATH_CRYPT_KEYS.replace('.','_'))


class DataCrypt(Crypt):
    def __init__(self):
        return super().__init__(name=PATH_CRYPT_DATA.replace('.','_'))




if __name__=='__main__':
    crypt = Crypt('testt')

    print(crypt.set('hellothere',b'ryan'))

    # print(crypt.get(b'hello there'))