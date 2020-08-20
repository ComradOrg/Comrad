import time
from itertools import takewhile
import operator
from collections import OrderedDict
from abc import abstractmethod, ABC

def xprint(*xx):
    raise Exception('\n'.join(str(x) for x in xx)) 



class IStorage(ABC):
    """
    Local storage for this node.
    IStorage implementations of get must return the same type as put in by set
    """

    @abstractmethod
    def __setitem__(self, key, value):
        """
        Set a key to the given value.
        """

    @abstractmethod
    def __getitem__(self, key):
        """
        Get the given key.  If item doesn't exist, raises C{KeyError}
        """

    @abstractmethod
    def get(self, key, default=None):
        """
        Get given key.  If not found, return default.
        """

    @abstractmethod
    def iter_older_than(self, seconds_old):
        """
        Return the an iterator over (key, value) tuples for items older
        than the given secondsOld.
        """

    @abstractmethod
    def __iter__(self):
        """
        Get the iterator for this storage, should yield tuple of (key, value)
        """


class ForgetfulStorage(IStorage):
    def __init__(self, ttl=604800):
        """
        By default, max age is a week.
        """
        self.data = OrderedDict()
        self.ttl = ttl

    def __setitem__(self, key, value):
        if key in self.data:
            del self.data[key]
        self.data[key] = (time.monotonic(), value)
        self.cull()

    def cull(self):
        for _, _ in self.iter_older_than(self.ttl):
            self.data.popitem(last=False)

    def get(self, key, default=None):
        self.cull()
        if key in self.data:
            return self[key]
        return default

    def __getitem__(self, key):
        self.cull()
        return self.data[key][1]

    def __repr__(self):
        self.cull()
        return repr(self.data)

    def iter_older_than(self, seconds_old):
        min_birthday = time.monotonic() - seconds_old
        zipped = self._triple_iter()
        matches = takewhile(lambda r: min_birthday >= r[1], zipped)
        return list(map(operator.itemgetter(0, 2), matches))

    def _triple_iter(self):
        ikeys = self.data.keys()
        ibirthday = map(operator.itemgetter(0), self.data.values())
        ivalues = map(operator.itemgetter(1), self.data.values())
        return zip(ikeys, ibirthday, ivalues)

    def __iter__(self):
        self.cull()
        ikeys = self.data.keys()
        ivalues = map(operator.itemgetter(1), self.data.values())
        return zip(ikeys, ivalues)











class HalfForgetfulStorage(ForgetfulStorage):
    def __init__(self, fn='data.db', ttl=604800, log=print):
        """
        By default, max age is a week.
        """
        self.fn=fn
        self.log=log
        
        import pickledb
        self.data = pickledb.load(self.fn,False)
        self.ttl = ttl

    def iter_older_than(self, seconds_old):
        return []

    def cull(self):
        pass

    def keys(self):
        return self.data.getall()

    def __len__(self):
        return len(self.keys())

    def __setitem__(self, key, value):
        stop
        self.set(key,value)

    def set(self, key,value):# try:
        sofar = self.data.get(key)
        if not sofar: sofar=[]
        xprint('SOFAR',sofar)
        #sofar = [sofar] if sofar and type(sofar)!=list else []
        print('SOFAR',sofar)
        newdat = (time.monotonic(), value)
        newval = sofar + [newdat]
        print('NEWVAL',newval)
        #del self.data[key]
        #self.data[key]=newval
        
        self.data.set(key,newval)
        self.data.dump()
        
        print('VALUE IS NOW'+str(self.data.get(key)))


    def get(self, key, default=None):
        # print(f'??!?\n{key}\n{self.data[key]}')
        # return self.data[key][1]
        # (skip time part of tuple)
        val=[]
        try:
            val=self.data.get(key)
            self.log('VALLLL',val)
        except KeyError:
            pass
        if type(val)!=list: val=[val]
        data_list = val
        self.log('data_list =',data_list)
        return [dat for dat in data_list]


    def __getitem__(self, key):
        return self.get(key)
        
        #return data_list
