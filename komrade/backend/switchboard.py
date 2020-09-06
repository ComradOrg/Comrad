# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *

# external imports
from flask import Flask, request, jsonify
from flask_classful import FlaskView




OPERATOR = None
TELEPHONE = None
from flask_classful import FlaskView, route

class TheSwitchboard(FlaskView, Logger):
    #default_methods = ['POST']

    def get(self,msg):
        self.log('Incoming call!:',msg)

        if not msg:
            self.log('empty request!')
            return OPERATOR_INTERCEPT_MESSAGE

        # unenescape
        msg = msg.replace('_','/')
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

        # then try to split
        # try:
        #     unencr_data,

        # # then try to unwrap top level encryption
        # try:
        #     data = SMessage(OPERATOR.privkey_, TELEPHONE.pubkey_).unwrap(data)
        #     self.log('decrypted data:',data)
        # except ThemisError:
        #     self.log('not really from the telephone?')
        #     return OPERATOR_INTERCEPT_MESSAGE

        # # step 3: give to The Operator
        try:
            # return 'Success! your message was: '+str(data)
            res = OPERATOR.route(data)
            return res
        except Exception as e:
            self.log('got exception!!',e)
            return OPERATOR_INTERCEPT_MESSAGE

        # return response to caller
        return OPERATOR_INTERCEPT_MESSAGE

def run_forever(port='8080'):
    global OPERATOR,TELEPHONE
    OPERATOR = TheOperator()
    TELEPHONE = TheTelephone()
    app = Flask(__name__)
    TheSwitchboard.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=True, port=port, host='0.0.0.0')