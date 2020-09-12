class KomradeException(Exception): pass

# make sure komrade is on path
import sys,os
sys.path.append(os.path.dirname(__file__))


def logger():
    import logging
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s]\n%(message)s\n')
    handler.setFormatter(formatter)
    logger = logging.getLogger('komrade')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

LOG = None

def log(*x):
    global LOG
    if not LOG: LOG=logger().debug

    tolog=' '.join(str(_) for _ in x)
    LOG(tolog)

def clear_screen():
    import os
    # pass
    os.system('cls' if os.name == 'nt' else 'clear')

def do_pause():
    try:
        input('')
    except KeyboardInterrupt:
        exit('\n\nGoodbye.')


def dict_format(d, tab=0):
    def reppr(v):
        if type(v)==bytes and not isBase64(v):
            return b64encode(v)
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
from komrade.constants import *
class Logger(object):
    def log(self,*x,pause=PAUSE_LOGGER,clear=PAUSE_LOGGER):
        if not SHOW_LOG: return
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        mytype = type(self).__name__
        caller = calframe[1][3]
        log(f'[{mytype}.{caller}()]\n\n',*x)

        # try:
        if pause: do_pause()
        if pause: clear_screen()
        # except KeyboardInterrupt:
        # exit()

    def print(*x,width=STATUS_LINE_WIDTH,end='\n',indent=1,ret=False,scan=False,**y):
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
                self.print(para,flush=True,end=end if end else '\n',scan=scan,indent=indent)
                paras+=[para]  
                do_pause()
            else:
                self.print(para,flush=True,end=end if end else '\n',scan=scan,indent=indent)
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
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except binascii.Error:
        return False




def hashish(binary_data):
    import hashlib
    return hashlib.sha256(binary_data).hexdigest()


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




def scan_print(xstr,min_pause=0,max_pause=.01,speed=1):
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