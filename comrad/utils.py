class ComradException(Exception): pass

# make sure comrad is on path
import sys,os
sys.path.append(os.path.dirname(__file__))

from logging import Handler
class CallbackHandler(Handler):
    def __init__(self,callbacks={},*x,**y):
        super().__init__(*x,**y)
        self._callbacks=callbacks
    def emit(self, record):
        # print(record)
        # stop
        # print('!!!!',record.msg, record.args)
        from torpy.documents.network_status import Router

        for arg in record.args:
            if type(arg)==Router:
                print('! Found router:',record.msg % record.args)
        # if len(record.args)==1 and type(record.args[0])==Router:
            # print('! Router:',record.msg,record.args[0].nickname)

        pass
        
        #log_entry = self.format(record)
        #return requests.post('http://example.com:8080/',
        #                     log_entry, headers={"Content-type": "application/json"}).content


def logger(name=__name__):
    import logging
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s]\n%(message)s\n')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

LOG = logger().info

def log(*x,off=False,**y):
    global LOG
    #if not LOG: LOG=logger().debug
    if not LOG: LOG=print
    tolog=' '.join(str(_) for _ in x)
    
    if not off:
        LOG(tolog)

    if SAVE_LOGS:
        path_log = os.path.join(PATH_LOG_OUTPUT,date_today()+'.log')
        with open(path_log,'a') as of:
            of.write('\n'+tolog+'\n')

from comrad.constants import CLI_WIDTH
def wrapp(*msgs,prefix='',min_prefix_len=0,width=CLI_WIDTH,use_prefix=False):
    blank=' '*(len(prefix) if len(prefix)>min_prefix_len else min_prefix_len)
    total_msg=[]
    for i,msg in enumerate(msgs):
        if not msg: msg=''
        msg=msg.replace('\r\n','\n').replace('\r','\n')
        for ii,ln in enumerate(msg.split('\n')):
            if not ln:
                total_msg+=['']
            ln_wrap=tw.wrap(ln,width-len(prefix))
            for iii,lnw in enumerate(ln_wrap):
                prfx=prefix + (' '*(len(blank)-len(prefix))) if (not i and not ii and not iii and use_prefix) else blank
                x=prfx+lnw
                total_msg+=[x]
    return '\n'.join(total_msg)




def clear_screen():
    import os
    # pass
    os.system('cls' if os.name == 'nt' else 'clear')

def do_pause():
    try:
        input('')
    except KeyboardInterrupt:
        exit('\n\nGoodbye.')

import textwrap as tw
def dict_format(d, tab=0):
    def reppr(v):
        if type(v)==bytes:
            if not isBase64(v):
                v=b64encode(v)
            v=v.decode()
            # v='\n'.join(tw.wrap(v,10))
        return v

    s = ['{\n\n']
    for k,v in sorted(d.items()):
        v=reppr(v)
        #print(k,v,type(v))

        if isinstance(v, dict):
            v = dict_format(v, tab+1)
        else:
            v = repr(v)

        
        # s.append('%s%r: %s (%s),\n' % ('  '*tab, k, v, type(v).__name__))
        s.append('%s%r: %s,\n\n' % ('  '*tab, k, reppr(v)))
    s.append('%s}' % ('  '*(tab-2)))
    return ''.join(s)

import inspect,time
from comrad.constants import *
class Logger(object):
    def __init__(self,callbacks={}):
        self._callbacks=callbacks

    @property
    def off(self):
        x=os.environ.get('COMRAD_SHOW_LOG')
        if x is not None:
            x=x.strip().lower()
            return x in {'n','0','false'}
        return not SHOW_LOG

    def hide_log(self):
        os.environ['COMRAD_SHOW_LOG']='0'
    def show_log(self):
        os.environ['COMRAD_SHOW_LOG']='1'
    def toggle_log(self):
        self.show_log() if self.off else self.hide_log()

    def log(self,*x,pause=PAUSE_LOGGER,clear=CLEAR_LOGGER,**y):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        mytype = type(self).__name__
        caller = calframe[1][3]
        x=list(x)
        x.insert(0,f'[{mytype}.{caller}()]')
        log(
            # .center(CLI_WIDTH) + '\n\n',
            *x,

            off=self.off    
        )

        # try:
        if pause: do_pause()
        if clear: clear_screen()
        # except KeyboardInterrupt:
        # exit()

    def printt(*x,width=STATUS_LINE_WIDTH,end='\n',indent=1,ret=False,scan=False,**y):
        if not scan and not width:
            print(*x,end=end,**y)
        else:
            import textwrap as tw
            xs=end.join(str(xx) for xx in x if type(xx)==str)
            if width:
                xw = [_.strip() for _ in tw.wrap(xs,width=width)]
                # xw = [_ for _ in tw.wrap(xs,width=width)]
                xs=end.join(xw)
            xs = tw.indent(xs,' '*indent)
            if ret: return xs
            print(xs) if scan==False else scan_print(xs)

    def status(self,*msg,pause=True,clear=False,ticks=[],tab=2,speed=10,end=None,indent=0,width=80,scan=False):
        import random
        if not SHOW_STATUS: return
        # if len(msg)==1 and type(msg[0])==str:
            # msg=[x for x in msg[0].split('\n\n')]
        if clear: clear_screen()
        paras=[]
        res={}
        for para in msg:
            plen = para if type(para)==int or type(para)==float else None
            if type(para) in {int,float}:
                plen=int(para)
                # print()
                print(' '*indent,end='',flush=True)
                for i in range(plen):
                    tick = ticks[i] if i<len(ticks) else '.'
                    print(tick,end=end if end else ' ',flush=True) #,scan=scan)
                    # time.sleep(random.random() / speed)
                    time.sleep(random.uniform(0.05,0.2))
                # print()
            elif para is None:
                clear_screen()
            elif para is False:
                do_pause()
            elif para is True:
                print()
            elif type(para) is set: # logo/image
                pl = [x for x in para if type(x)==str]
                txt=pl[0]
                speed =[x for x in para if type(x) in {int,float}]
                speed = speed[0] if speed else 1
                if True in para:
                    scan_print(txt,speed=speed)
                else:
                    print(txt,end=end)
            elif type(para) is tuple:
                k=para[0]
                q=para[1]
                f=para[2] if len(para)>2 else input
                ans=None
                while not ans:
                    ans=f(q).strip()
                res[k]=ans
            elif type(para) is dict:
                print(dict_format(para,tab=tab))
            elif pause:
                self.printt(para,flush=True,end=end if end else '\n',scan=scan,indent=indent)
                paras+=[para]  
                do_pause()
            else:
                self.printt(para,flush=True,end=end if end else '\n',scan=scan,indent=indent)
                paras+=[para]    
        return {'paras':paras, 'vals':res}

import binascii,base64
def isBase64(sb):
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            return False
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except binascii.Error:
        return False


import inspect,functools
def get_class_that_defined_method(meth):
    if isinstance(meth, functools.partial):
        return get_class_that_defined_method(meth.func)
    if inspect.ismethod(meth) or (inspect.isbuiltin(meth) and getattr(meth, '__self__', None) is not None and getattr(meth.__self__, '__class__', None)):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = getattr(meth, '__func__', meth)  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],
                      None)
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)  # handle special descriptor objects

def d2b64(d):
    d2={}
    for k,v in d.items():
        if type(v)==bytes and not isBase64(v):
            d2[k]=b64encode(v)
        else:
            d2[k]=v
    return d2

def b64enc(x):
    if x is None: return b''
    if type(x) not in {str,bytes}: return x
    if type(x)==str: x=x.encode()
    if not isBase64(x): x=b64encode(x)
    return x

def b64dec(x):
    if x is None: return b''
    if type(x) not in {str,bytes}: return x
    if type(x)==str: x=x.encode()
    if isBase64(x): x=b64decode(x)
    return x

def b64enc_s(x):
    return b64enc(x).decode()



def hashish(binary_data):
    import hashlib
    return hashlib.sha256(binary_data).hexdigest()

def create_secret():
    if not os.path.exists(PATH_CRYPT_SECRET):    
        secret = get_random_binary_id()
        from comrad.backend.keymaker import make_key_discreet
        print('shhh! creating secret:',make_key_discreet(secret))
        with open(PATH_CRYPT_SECRET,'wb') as of:
            of.write(secret)

def hasher(dat,secret=None):
    import hashlib
    if not secret:
        create_secret()
        with open(PATH_CRYPT_SECRET,'rb') as f:
            secret = f.read()
    if type(dat)==str:
        dat=dat.encode()

    # print(dat,secret[:10])
    return b64encode(hashlib.sha256(dat + secret).hexdigest().encode()).decode()


from base64 import b64encode,b64decode
import ujson as json
import pickle
def package_for_transmission(data_json):
    # print('package_for_transmission.data_json =',data_json)
    

    data_json_b = pickle.dumps(data_json)
    # print('data_json_b??')
    # print('package_for_transmission.data_json_b =',data_json_bstr)
    return data_json_b


def dejsonize(dict):
    for k,v in dict.items():
        if type(v)==str and isBase64(v):
            dict[k]=v.encode()
        # if type(v)==bytes and isBase64(v):
            # dict[k]=b64decode(v)
        elif type(v)==dict:
            dict[k]=dejsonize(v)
    return dict

def unpackage_from_transmission(data_json_b64):
    # print('unpackage_from_transmission.data_json_b64 =',data_json_b64)
    data_json_b = b64decode(data_json_b64)
    # print('unpackage_from_transmission.data_json_bstr =',data_json_b)
    
    data_json = pickle.loads(data_json_b)
    # print('unpackage_from_transmission.data_json =',data_json)

    # data_json_dejson = dejsonize(data_json)
    # print('unpackage_from_transmission.data_json =',data_json_dejson)

    return data_json


def get_random_id():
    import uuid
    return uuid.uuid4().hex

def get_random_binary_id():
    import base64
    idstr = get_random_id()
    return base64.b64encode(idstr.encode())



# Recursive dictionary merge
# https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
#
# Copyright (C) 2016 Paul Durivage <pauldurivage+github@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import collections

def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]



def capture_stdout(func):
    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        func()
    out = f.getvalue()
    return out




def scan_print(xstr,min_pause=0,max_pause=.01,speed=2):
    import random,time
    for c in xstr:
        print(c,end='',flush=True)
        naptime=random.uniform(min_pause, max_pause / speed)
        time.sleep(naptime)
        # time.sleep()
        


def get_qr_str(data):
    import qrcode
    qr=qrcode.QRCode()
    qr.add_data(data)
    ascii = capture_stdout(qr.print_ascii)
    ascii = ascii[:-1] # removing last line break
    return '\n    ' + ascii.strip()



def indent_str(x,n):
    import textwrap as tw
    return  tw.indent(x,' '*n)


def date_today():
    import datetime
    dt = datetime.datetime.today()
    return f'{dt.year}-{str(dt.month).zfill(2)}-{dt.day}'

def multiline_input(msg=None):
    # if msg:
        # print(msg,end=' ')
    
    contents = []
    i=-1
    while True:
        i+=1
        try:
            line = input(msg if msg and not i else "") #.decode('utf-8',errors='ignore')
            contents.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            contents=''
            break

    txt="\n".join(contents) if contents else contents
    return txt



class ThreadExecutor:
    """In most cases, you can just use the 'execute' instance as a
    function, i.e. y = await execute(f, a, b, k=c) => run f(a, b, k=c) in
    the executor, assign result to y. The defaults can be changed, though,
    with your own instantiation of Executor, i.e. execute =
    Executor(nthreads=4)"""
    def __init__(self, loop=None, nthreads=1):
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        if not loop: loop=asyncio.get_event_loop()
        
        self._ex = ThreadPoolExecutor(nthreads)
        self._loop = loop

    def __call__(self, f, *args, **kw):
        from functools import partial
        return self._loop.run_in_executor(self._ex, partial(f, *args, **kw))

# execute = Executor()

# ...

# def cpu_bound_operation(t, alpha=30):
#     sleep(t)
#     return 20*alpha

# async def main():
#     y = await execute(cpu_bound_operation, 5, alpha=-2)

# loop.run_until_complete(main())