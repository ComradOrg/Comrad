# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *

# external imports
from flask import Flask, request, jsonify
from flask_classful import FlaskView

class TheSwitchboard(FlaskView, Logger):
    default_methods = ['GET']
    excluded_methods = ['phone','op','send']

    @property
    def op(self):
        from komrade.backend.the_operator import TheOperator
        if type(self)==TheOperator: return self
        if hasattr(self,'_op'): return self._op
        global OPERATOR,OPERATOR_KEYCHAIN
        if OPERATOR: return OPERATOR
        self._op=OPERATOR=TheOperator()        
        return OPERATOR

    
    def get(self,data_b64_str_esc):
        self.log('Incoming call!:',data_b64_str_esc)
        if not data_b64_str_esc:
            self.log('empty request!')
            return OPERATOR_INTERCEPT_MESSAGE
        
        # unenescape
        data_b64_str = data_b64_str_esc.replace('_','/')

        # encode to binary
        data_b64 = data_b64_str.encode()
        data_b = b64decode(data_b64)

        # ask operator to answer phone and request
        resp_data_b = self.op.answer_phone(data_b)

        # decode to str
        #resp_data_b64 = b64encode(resp_data_b)
        #resp_data_b64_str = resp_data_b64.decode()
        # resp_data_b64_str_esc = resp_data_b64_str.replace('/','_')

        # return as str
        #return resp_data_b64_str
        return resp_data_b

def run_forever(port='8080'):
    global OPERATOR,TELEPHONE,TELEPHONE_KEYCHAIN,OPERATOR_KEYCHAIN,OMEGA_KEY
    OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN,OMEGA_KEY=connect_phonelines()
    TELEPHONE = TheTelephone()
    OPERATOR = TheOperator()
    app = Flask(__name__)
    TheSwitchboard.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=False, port=port, host='0.0.0.0')