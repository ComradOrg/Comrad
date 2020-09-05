"""
There is only one operator!
Running on node prime.
"""
# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.operators.crypt import *
from komrade.operators.keymaker import *
from komrade.operators.mazes import *

# external imports
from flask import Flask, request, jsonify
from flask_classful import FlaskView



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
    def op(self):
        """
        Operator on the line.
        """
        if not hasattr(self,'_op'):
            self._op = TheOperatorOnThePhone(caller = self)
        return self._op

    def get_new_keys(self,pubkey_pass = None, privkey_pass = None, adminkey_pass = None):
        """
        This is the local caller's version.
        He never touches the encrypted keys. Only the Operator does!
        """

        # Get decryptor keys back from The Operator (one half of the Keymaker)
        keychain = self.op.forge_new_keys(self.name)
        self.log('create_keys() res from Operator? <-',keychain)

        # Now lock the decryptor keys away, sealing it with a password of memory!
        self.lock_new_keys(keychain)

class TheOperator(Operator):
    """
    The remote operator! Only one!
    """
    

    def __init__(self, name = 'TheOperator', passphrase=None):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """
        # init req paths
        if not os.path.exists(PATH_OPERATOR): os.makedirs(PATH_OPERATOR)


        if not passphrase:
            passphrase=getpass.getpass('Hello, this is the Operator speaking. What is the passphrase?\n> ')
        super().__init__(name,passphrase)

        ## boot up if necessary
         # Do I have my keys?
        have_keys = self.exists()
        self.log('I have my keys?',have_keys)
        # If not, forge them -- only once!
        if not have_keys:
            self.get_new_keys()

        # load keychain into memory
        self._keychain = self.keychain(force = True)


### ACTUAL PHONE CONNECTIONS
class TheOperatorOnThePhone(object):
    """
    API client class for Caller to interact with The Operator.
    """
    def __init__(self, caller):
        self.caller = caller

    @property
    def sess(self):
        """
        Get connection to Tor
        """
        if not hasattr(self,'_sess'):
            self._sess = get_tor_proxy_session()
        return self._sess

    def req(self,req_json={},req_data=None):
        req_json_s = jsonify(req_json)
        req_json_s.encode()
        
        # encrypt
        from_privkey = self.caller.privkey_
        to_pubkey = OPERATOR_PUBKEY
        encrypted_msg = SMessage(from_privkey, for_pubkey).wrap(msg_b64)
        return b64encode(encrypted_msg)

    def forge_new_keys(self, name, pubkey_is_public=False):
        req_json = {'name':name, 'pubkey_is_public':pubkey_is_public}
        req_json_s = jsonify(req_json)
        req_json_s_encr = SMessage()
        return self.sess.post(json=req_json)


OPERATOR = None
class TheSwitchboard(FlaskView):
    default_methods = ['POST']
        
    def forge_new_keys(self):
        content = request.json

        #return f'{name}\n{pubkey_is_public}\n{return_all_keys}'
    
    def something(self):
        return 'something'


def run_forever():
    

    global OPERATOR
    OPERATOR = TheOperator()
    app = Flask(__name__)
    TheSwitchboard.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=True, port=6999)



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
    print(pubkey_b64)
    

if __name__ == '__main__':
    #run_forever()
    test_op()