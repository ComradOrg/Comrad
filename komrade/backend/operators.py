# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *
from komrade.backend.keymaker import *
from komrade.backend.mazes import *
from komrade.backend.switchboard import *




class Operator(Keymaker):
    
    def __init__(self, name, passphrase=None):
        super().__init__(name=name,passphrase=passphrase)

    def boot(self,create=False):
         # Do I have my keys?
        have_keys = self.exists()
        
        # If not, forge them -- only once!
        if not have_keys and create:
            self.get_new_keys()

        # load keychain into memory
        self._keychain = self.keychain(force = True)



