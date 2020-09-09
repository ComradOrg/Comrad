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


import inspect
class Logger(object):
    def log(self,*x):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        mytype = type(self).__name__
        caller = calframe[1][3]
        log(f'\n[{mytype}.{caller}()]',*x)

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
    # print('package_for_transmission.data_json_b =',data_json_bstr)
    return b64encode(data_json_b)


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