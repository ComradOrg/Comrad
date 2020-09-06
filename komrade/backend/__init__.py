from .operators import *
from .callers import *
from .crypt import *
from .ether import *
from .keymaker import *
from .mazes import *

from .switchboard import *
from .the_operator import *
from .the_telephone import *





## can I even hope to succeed?
def get_builtin_keys():
    with open(PATH_BUILTIN_KEYCHAINS_ENCR,'rb') as f_encr, open(PATH_BUILTIN_KEYCHAINS_DECR,'rb') as f_decr:
        builtin_keychains_b_encr_b64=f_encr.read()
        builtin_keychains_b_decr_b64=f_decr.read()

        builtin_keychains_b_encr=b64decode(builtin_keychains_b_encr_b64)
        builtin_keychains_b_decr=b64decode(builtin_keychains_b_decr_b64)

        builtin_keychains_b = SCellSeal(key=builtin_keychains_b_decr).decrypt(builtin_keychains_b_encr)
        builtin_keychains_s = builtin_keychains_b.decode('utf-8')
        builtin_keychains = json.loads(builtin_keychains_s)

        # filter
        print(builtin_keychains)
        for name in builtin_keychains:
            for keyname in builtin_keychains[name]:
                v=builtin_keychains[name][keyname]
                builtin_keychains[name][keyname] = v.encode('utf-8')
        
        return builtin_keychains

