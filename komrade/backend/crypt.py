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



LOG_GET_SET = True



class Crypt(Logger):
    def __init__(self,name=None,fn=None,cell=None,init_d=None):
        if not name and fn: name=os.path.basename(fn).replace('.','_')

        self.name,self.fn,self.cell = name,fn,cell
        self.store = FilesystemStore(self.fn)
        if init_d:
            for k,v in init_d.items():
                try:
                    self.store.put(k,v)
                except OSError as e:
                    self.log('!!',e)
                    self.log('!! key ->',k)
                    self.log('!! val ->',v)
                    raise KomradeException()
                    

    def log(self,*x):
        if LOG_GET_SET:
            super().log(*x)
        
    def hash(self,binary_data):
        return hashlib.sha256(binary_data).hexdigest()
        # return zlib.adler32(binary_data)

    def force_binary(self,k_b):
        # if k_b is None: return b''
        if type(k_b)==str: k_b=k_b.encode()
        if type(k_b)!=bytes: k_b=k_b.decode()
        return k_b

    def package_key(self,k,prefix=''):
        self.log('k???',type(k),k)
        self.log('prefix???',type(prefix),prefix)
        k_b = self.force_binary(k)
        self.log(type(k_b),k_b)
        # k_s = k_b.decode()
        # self.log(type(k_s),k_s)
        # k_s2 = prefix + k_s
        # self.log(type(k_s2),k_s2)
        # k_b2 = k_s2.encode()
        k_b2 = self.force_binary(prefix) + k_b
        self.log('k_b2',type(k_b2),k_b2)
        # k_b = self.cell.encrypt(k_b)
        # prefix_b = self.force_binary(prefix)
        
        return k_b2

    def package_val(self,k):
        k_b = self.force_binary(k)
        if self.cell is not None: k_b = self.cell.encrypt(k_b)
        return k_b


    def unpackage_val(self,k_b):
        try:
            if self.cell is not None: k_b = self.cell.decrypt(k_b)
        except ThemisError:
            pass
        return k_b


    def set(self,k,v,prefix=''):
        self.log('set() k -->',prefix,k)
        k_b=self.package_key(k,prefix=prefix)
        self.log('set() k_b -->',k_b)
        k_b_hash = self.hash(k_b)
        self.log('k_b_hash',type(k_b_hash),k_b_hash)

        self.log('set() v -->',v)
        v_b=self.package_val(v)
        self.log(f'set(\n\t{prefix}{k},\n\t{k_b}\n\t{k_b_hash}\n\t\n\t{v_b}\n)\n')
        # stop
        # stop
        
        return self.store.put(k_b_hash,v_b)

    def exists(self,k,prefix=''):
        return bool(self.get(k,prefix=prefix))

    def get(self,k,prefix=''):
        self.log('k1? -->',prefix,k)
        k_b=self.package_key(k,prefix=prefix)
        self.log('k2? -->',k_b)
        k_b_hash = self.hash(k_b)
        self.log('k_b_hash',type(k_b_hash),k_b_hash)

        try:
            v=self.store.get(k_b_hash)
        except KeyError:
            return None
        self.log('v? -->',v)
        v_b=self.unpackage_val(v)
        self.log('v_b?',v_b)
        self.log('get()',k_b,'-->',v_b)
        return v_b


class KeyCrypt(Crypt):
    def __init__(self):
        return super().__init__(name=PATH_CRYPT_CA_KEYS.replace('.','_'))


class DataCrypt(Crypt):
    def __init__(self):
        return super().__init__(name=PATH_CRYPT_CA_DATA.replace('.','_'))


from collections import defaultdict
class CryptMemory(Crypt):
    def __init__(self):
        self.data = defaultdict(None) 
        self.crypt = defaultdict(None)
        self.cell = None
    
    def set(self,k,v,prefix=''):
        k_b=self.package_key(k,prefix=prefix)
        v_b=self.package_val(v)
        self.data[k]=v_b
        self.crypt[k_b]=v_b
    


if __name__=='__main__':
    crypt = Crypt('testt')

    print(crypt.set('hellothere',b'ryan'))

    # print(crypt.get(b'hello there'))