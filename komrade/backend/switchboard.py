# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *

# external imports
from flask import Flask, request, jsonify
from flask_classful import FlaskView

# PATH_OPERATOR_WEB_KEYS_URI = hashish(b'keys')
# PATH_OPERATOR_WEB_KEYS_FILE = f'/home/ryan/www/website-komrade/.builtin.keys'
# PATH_OPERATOR_WEB_KEYS_URL = f'http://{KOMRADE_ONION}/.builtin.keys'

# print(PATH_OPERATOR_WEB_KEYS_URL)


OPERATOR = None
TELEPHONE = None
from flask_classful import FlaskView, route

class TheSwitchboard(FlaskView, Logger):
    default_methods = ['GET']
    excluded_methods = ['phone','op','send']

    @route('/.builtin.keys/')
    def keys(self):
        if not os.path.exists(PATH_OPERATOR_WEB_KEYS_FILE):
            self.log('no keys file exists!',PATH_OPERATOR_WEB_KEYS_FILE)
            return OPERATOR_INTERCEPT_MESSAGE
        with open(PATH_OPERATOR_WEB_KEYS_FILE,'rb') as  f:
            return f.read()

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
    global OPERATOR,TELEPHONE,TELEPHONE_KEYCHAIN,OPERATOR_KEYCHAIN
    OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN=connect_phonelines()
    TELEPHONE = TheTelephone()
    OPERATOR = TheOperator()
    app = Flask(__name__)
    TheSwitchboard.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=True, port=port, host='0.0.0.0')