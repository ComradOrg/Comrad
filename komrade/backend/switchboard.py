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
    default_methods = ['GET']
    excluded_methods = ['phone','op','send']

    @property
    def phone(self):
        global TELEPHONE
        from komrade.backend.the_telephone import TheTelephone
        if not TELEPHONE: TELEPHONE=TheTelephone()
        return TELEPHONE

    @property
    def op(self):
        global OPERATOR
        from komrade.backend.the_operator import TheOperator
        if not OPERATOR: OPERATOR=TheOperator()
        return OPERATOR

    def send(self,res):
        return res

    def route(self,msg):
        # give to The Operator
        try:
            self.log('Success! your message was: '+str(msg))
            res = self.op.recv(msg)
            self.log('Your return result should be:',res)
            return self.send(res)
        except AssertionError as e:
            self.log('got exception!!',e)
        return OPERATOR_INTERCEPT_MESSAGE
    
    def get(self,msg):
        self.log('Incoming call!:',msg)
        if not msg:
            self.log('empty request!')
            return OPERATOR_INTERCEPT_MESSAGE
        # unenescape
        msg = msg.replace('_','/')
        return self.route(msg)

def run_forever(port='8080'):
    global OPERATOR,TELEPHONE
    TELEPHONE = TheTelephone(allow_builtin=False)
    OPERATOR = TheOperator(allow_builtin=False)
    app = Flask(__name__)
    TheSwitchboard.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=True, port=port, host='0.0.0.0')