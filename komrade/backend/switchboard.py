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
    
    def get(self,msg):
        self.log('Incoming call!:',msg)
        if not msg:
            self.log('empty request!')
            return OPERATOR_INTERCEPT_MESSAGE
        # unenescape
        msg = msg.replace('_','/')
        str_msg_from_op = self.op.route(msg)
        str_msg_from_op = msg.replace('_','/')
        self.log('Switchboard got msg back from Operator:',str_msg_from_op)
        return str_msg_from_op

def run_forever(port='8080'):
    global OPERATOR,TELEPHONE,TELEPHONE_KEYCHAIN,OPERATOR_KEYCHAIN
    OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN=connect_phonelines()
    TELEPHONE = TheTelephone()
    OPERATOR = TheOperator()
    app = Flask(__name__)
    TheSwitchboard.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=False, port=port, host='0.0.0.0')