# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *
from komrade.backend.keymaker import *
from komrade.backend.mazes import *
from komrade.backend.switchboard import *




class Operator(Keymaker):
    
    def __init__(self, name, passphrase=None, path_crypt_keys=PATH_CRYPT_CA_KEYS, path_crypt_data=PATH_CRYPT_CA_DATA):
        super().__init__(name=name,passphrase=passphrase, path_crypt_keys=path_crypt_keys, path_crypt_data=path_crypt_data)
        self.boot(create=False)

    def boot(self,create=False):
         # Do I have my keys?
        have_keys = self.exists()
        
        # If not, forge them -- only once!
        if not have_keys and create:
            self.get_new_keys()

        # load keychain into memory
        self._keychain = self.keychain(force = True)

    
    # ### BASE STORAGE
    # @property
    # def crypt_keys(self):
    #     if not hasattr(self,'_crypt_keys'):
    #         self._crypt_keys = Crypt(fn=self.path_crypt_keys)
    #     return self._crypt_keys

