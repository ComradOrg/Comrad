"""
There is only one operator!
Running on node prime.
"""
# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *
from komrade.backend.keymaker import *
from komrade.backend.mazes import *


OPERATOR_NAME = 'TheOperator'
TELEPHONE_NAME = 'TheTelephone'

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



class Caller(Operator):
    """
    Variant of an Operator which handles local keys and keymaking.
    """

    @property
    def phone(self):
        """
        Operator on the line.
        """
        if not hasattr(self,'_phone'):
            self._phone = TheTelephone(caller = self)
        return self._phone

    def get_new_keys(self,pubkey_pass = None, privkey_pass = None, adminkey_pass = None):
        """
        This is the local caller's version.
        He never touches the encrypted keys. Only the Operator does!
        """

        # Get decryptor keys back from The Operator (one half of the Keymaker)
        keychain = self.forge_new_keys(self.name)
        self.log('create_keys() res from Operator? <-',keychain)

        # Now lock the decryptor keys away, sealing it with a password of memory!
        self.lock_new_keys(keychain)

class TheOperator(Operator):
    """
    The remote operator! Only one!
    """
    

    def __init__(self, name = OPERATOR_NAME, passphrase='acc'):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """
        # init req paths
        if not os.path.exists(PATH_OPERATOR): os.makedirs(PATH_OPERATOR)
        if not passphrase:
            passphrase=getpass.getpass('Hello, this is the Operator speaking. What is the passphrase?\n> ')
        super().__init__(name,passphrase)

    def route(self, data):
        # step 1 split:
        data_unencr,data_encr = data.split(BSEP)
        if data_encr and 'name' in data_unencr:
            name=data_unencr['name']
            keychain=data_unencr.get('keychain',{})

            # decrypt using this user's pubkey on record
            caller = Operator(name)
            from_pubkey = user.pubkey(keychain=keychain)
            data_unencr2 = SMessage(OPERATOR.privkey_, from_pubkey).unwrap(data_encr)

            if type(data_unencr)==dict and type(data_unencr2)==dict:
                data = data_unencr
                dict_merge(data_unencr2, data)
            else:
                data=(data_unencr,data_unencr2)
        else:
            data = data_unencr

        print(data)


def init_operators():
    op = Operator(name=OPERATOR_NAME)
    phone = Operator(name=TELEPHONE_NAME)

    op.get_new_keys()
    phone.get_new_keys()

    op_pub = op.pubkey_
    phone_pub = phone.pubkey_
    phone_priv = phone.privkey_

    print('OPERATOR_PUBKEY =',b64encode(op_pub))
    print('TELEPHONE_PUBKEY =',b64encode(phone_pub))
    print('TELEPHONE_PRIVKEY =',b64encode(phone_priv))
    

def test_op():
    op = TheOperator()
    #op.boot()
    #pubkey = op.keychain()['pubkey']
    #pubkey_b64 = b64encode(pubkey)
    #print(pubkey_b64)
    keychain = op.keychain(force=True)
    from pprint import pprint
    pprint(keychain)
    
    pubkey = op.keychain()['pubkey']
    pubkey_b64 = b64encode(pubkey)
    print(pubkey)
    
def test_call():
    caller = Operator('marx3') #Caller('marx')
    # caller.boot(create=True)
    # print(caller.keychain())
    phone = TheTelephone(caller=caller)
    res = phone.req({'name':'marx', 'pubkey_is_public':True})
    print(res)

if __name__ == '__main__':
    #run_forever()
    # test_op()
    # init_operators()
    test_call()