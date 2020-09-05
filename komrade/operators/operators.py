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


### ACTUAL PHONE CONNECTIONS
class TheTelephone(Logger):
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

    def req(self,json_coming_from_phone={},json_coming_from_caller={}):
        # Two parts of every request:
        
        # 1) only overall encryption layer E2EE Telephone -> Operator:

        req_data = []        
        if json_coming_from_phone:
            json_coming_from_phone_s = json.dumps(json_coming_from_phone)
            json_coming_from_phone_b = json_coming_from_phone_s.encode()
            #json_coming_from_phone_b_encr = SMessage(TELEPHONE_PRIVKEY,OPERATOR_PUBKEY).wrap(json_coming_from_phone_b)
        else:
            json_coming_from_phone_b=b''

        # 2) (optional) extra E2EE encrypted layer Caller -> Operator
        if json_coming_from_caller:
            json_coming_from_caller_s = json.dumps(json_coming_from_caller)
            json_coming_from_caller_b = json_coming_from_caller_s.encode()
            json_coming_from_caller_b_encr = SMessage(self.caller.privkey_,OPERATOR_PUBKEY).wrap(json_coming_from_caller_b)
        else:
            json_coming_from_caller_b_encr = b''

        # encrypt whole package E2EE, Telephone to Operator
        req_data = json_coming_from_phone_b + BSEP + json_coming_from_caller_b_encr
        req_data_encr = SMessage(TELEPHONE_PRIVKEY, OPERATOR_PUBKEY).wrap(req_data)
        req_data_encr_b64 = b64encode(req_data_encr)
        self.log('req_data_encr_b64 <--',req_data_encr_b64)

        # send!
        res = self.sess.post(OPERATOR_API_URL, data=req_data_encr_b64)
        self.log('result from operator?',res)

        return res


    def forge_new_keys(self, name, pubkey_is_public=False):
        req_json = {'name':name, 'pubkey_is_public':pubkey_is_public}
        req_json_s = jsonify(req_json)
        req_json_s_encr = SMessage()
        return self.sess.post(json=req_json)


OPERATOR = None
class TheSwitchboard(FlaskView, Logger):
    default_methods = ['POST']
        
    def req(self):
        data = request.data
        self.log('incoming_data! <--',data)

        # step 1: decode
        data = b64decode(data)
        self.log('decoded data:',data)

        # step 2: decrypt from phone
        data = SMessage(OPERATOR.privkey_, TELEPHONE_PUBKEY).unwrap(data)
        self.log('decrypted data:',data)

        return data

def run_forever():
    global OPERATOR
    OPERATOR = TheOperator()
    app = Flask(__name__)
    TheSwitchboard.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=True, port=6999, host='0.0.0.0')

def init_operators():
    op = Operator(name=OPERATOR_NAME)
    phone = Operator(name=TELEPHONE_NAME)

    op.get_new_keys()
    phone.get_new_keys()

    op_pub = op.pubkey_
    phone_pub = phone.pubkey_
    phone_priv = phone.privkey_

    print('OPERATOR_PUBKEY',op_pub)
    print('TELEPHONE_PUBKEY =',phone_pub)
    print('TELEPHONE_PRIVKEY =',phone_priv)
    

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