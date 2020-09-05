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
    def op_pubkey(self):
        return b64decode(OPERATOR_PUBKEY)

    def dial_operator(self,msg):
        URL = OPERATOR_API_URL + msg
        r=tor_request_in_python(OPERATOR_API_URL)
        print(r)
        print(r.text)
        return r
        
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
            op_pubkey
            json_coming_from_caller_b_encr = SMessage(self.caller.privkey_,self.op_pubkey).wrap(json_coming_from_caller_b)
        else:
            json_coming_from_caller_b_encr = b''

        # encrypt whole package E2EE, Telephone to Operator
        req_data = json_coming_from_phone_b + BSEP + json_coming_from_caller_b_encr
        req_data_encr = SMessage(
            b64decode(TELEPHONE_PRIVKEY),
            b64decode(OPERATOR_PUBKEY)
        ).wrap(req_data)
        req_data_encr_b64 = b64encode(req_data_encr)
        self.log('req_data_encr_b64 <--',req_data_encr_b64)

        # send!
        req_data_encr_b64_str = req_data_encr_b64.decode('utf-8')
        res = self.dial_operator(req_data_encr_b64_str)
        self.log('result from operator?',res)
        return res


    def forge_new_keys(self, name, pubkey_is_public=False):
        req_json = {'name':name, 'pubkey_is_public':pubkey_is_public}
        req_json_s = jsonify(req_json)
        req_json_s_encr = SMessage()
        return self.sess.post(json=req_json)


OPERATOR = None
from flask_classful import FlaskView, route

class TheSwitchboard(FlaskView, Logger):
    #default_methods = ['POST']

    def get(self,msg):
        if not msg:
            self.log('empty request!')
            return OPERATOR_INTERCEPT_MESSAGE

        if not isBase64(msg):
            self.log('not valid input!')
            return OPERATOR_INTERCEPT_MESSAGE
        encr_b64_str = msg

        # first try to get from string to bytes
        self.log('incoming <--',encr_b64_str)
        try:
            encr_b64_b = encr_b64_str.encode('utf-8')
            self.log('encr_b64_b',encr_b64_b)
        except UnicodeEncodeError:
            self.log('not valid unicode?')
            return OPERATOR_INTERCEPT_MESSAGE

        # then try to get from b64 bytes to raw bytes
        try:
            data = b64decode(encr_b64_b)
            self.log('data',data)
            self.log(f'successfully understood input')
        except binascii.Error as e:
            self.log('not valid b64?')
            return OPERATOR_INTERCEPT_MESSAGE

        # then try to unwrap top level encryption
        try:
            tele_pubkey = b64decode(TELEPHONE_PUBKEY)
            data = SMessage(OPERATOR.privkey_, tele_pubkey).unwrap(data)
            self.log('decrypted data:',data)
        except ThemisError:
            self.log('not really from the telephone?')
            return OPERATOR_INTERCEPT_MESSAGE

        # step 3: give to The Operator
        try:
            return 'Success! your message was: '+str(data)
            res = OPERATOR.route(data)
            return res
        except Exception as e:
            self.log('got exception!!',e)
            return OPERATOR_INTERCEPT_MESSAGE

        # return response to caller
        return OPERATOR_INTERCEPT_MESSAGE

def run_forever(port='8080'):
    global OPERATOR
    OPERATOR = TheOperator()
    app = Flask(__name__)
    TheSwitchboard.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=True, port=port, host='0.0.0.0')