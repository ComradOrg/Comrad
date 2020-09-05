# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *
from komrade.backend.keymaker import *
from komrade.backend.mazes import *
from komrade.backend.operators import *

# external imports
from flask import Flask, request, jsonify
from flask_classful import FlaskView



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
        req_data_encr_b64_str = req_data_encr_b64.decode('utf-8')
        res = self.sess.post(OPERATOR_API_URL + req_data_encr_b64)
        self.log('result from operator?',res)
        return res


    def forge_new_keys(self, name, pubkey_is_public=False):
        req_json = {'name':name, 'pubkey_is_public':pubkey_is_public}
        req_json_s = jsonify(req_json)
        req_json_s_encr = SMessage()
        return self.sess.post(json=req_json)


OPERATOR = None
class TheSwitchboard(FlaskView, Logger):
    #default_methods = ['POST']

    #def get(self):
    #    return "We're sorry; we are unable to complete your call as dialed. Please check the number and dial again, or call your operator to help you."


    def get(self,encr_b64_str):
        # first try to get from string to bytes
        self.log('incoming <--',encr_b64_str)

        try:
            encr_b64_b = encr_b64_str.decode('utf-8')
            self.log('encr_b64_b',encr_b64_b)
            encr_b = b64decode(encr_b64_b)
            self.log('encr_b',encr_b)
            return encr_b
        except UnicodeDecodeError:
            return OPERATOR_INTERCEPT_MESSAGE

        if not encr_b64_str: return OPERATOR_INTERCEPT_MESSAGE
        

        data = request.data
        self.log('incoming_data! <--',data)

        # step 1: decode
        data = b64decode(data)
        self.log('decoded data:',data)

        # step 2: decrypt from phone
        data = SMessage(OPERATOR.privkey_, TELEPHONE_PUBKEY).unwrap(data)
        self.log('decrypted data:',data)

        # step 3: give to The Operator
        res = OPERATOR.route(data)

        # return response to caller
        return res

def run_forever(port='8080'):
    global OPERATOR
    OPERATOR = TheOperator()
    app = Flask(__name__)
    TheSwitchboard.register(app, route_base='/', route_prefix=None)
    app.run(debug=True, port=port, host='0.0.0.0')