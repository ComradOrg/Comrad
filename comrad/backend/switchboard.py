# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from comrad import *
from comrad.backend import *
from getpass import getpass

# external imports
from flask import Flask, request, jsonify
from flask_classful import FlaskView
OP_PASS = None

class TheSwitchboard(FlaskView, Logger):
    default_methods = ['GET']
    excluded_methods = ['phone','op','send','printt','log','status']

    @property
    def op(self):
        global OP_PASS
        from comrad.backend.the_operator import TheOperator
        if type(self)==TheOperator: return self
        if hasattr(self,'_op'): return self._op
        global OPERATOR,OPERATOR_KEYCHAIN
        if OPERATOR: return OPERATOR
        self._op=OPERATOR=TheOperator()
        return OPERATOR

    def post(self):
        clear_screen()
        from comrad.cli.artcode import ART_OLDPHONE4
        data_b=requests.data

        self.log(f'Incoming call! {ART_OLDPHONE4}: {data_b}')
        
        if not data_b:
            self.log('empty request!')
            return OPERATOR_INTERCEPT_MESSAGE
        
        # ask operator to answer phone and request
        resp_data_b = self.op.answer_phone(data_b)

        # decode to str
        self.log('about to send back -->',resp_data_b)
        return resp_data_b
    
    # def get(self,data_b64_str_esc):
    #     clear_screen()
    #     from comrad.cli.artcode import ART_OLDPHONE4
    #     # self.log(f'Incoming call!: {data_b64_str_esc}')
    #     if not data_b64_str_esc:
    #         self.log('empty request!')
    #         return OPERATOR_INTERCEPT_MESSAGE
        
    #     # unenescape
    #     data_b64_str = data_b64_str_esc.replace('_','/')

    #     # encode to binary
    #     data_b64 = data_b64_str.encode()
    #     data_b = b64decode(data_b64)

    #     # ask operator to answer phone and request
    #     resp_data_b = self.op.answer_phone(data_b)

    #     # decode to str
    #     resp_data_b64 = b64encode(resp_data_b)
    #     resp_data_b64_str = resp_data_b64.decode()

    #     # return as str
    #     return resp_data_b64_str

def run_forever(port='8080'):
    # global OP_PASS
    # OP_PASS = getpass('@op pass? ')
    TELEPHONE = TheTelephone()
    OPERATOR = TheOperator()
    # print(OPERATOR,'!?',OPERATOR.keychain())
    app = Flask(__name__)
    TheSwitchboard.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=True, port=port, host='0.0.0.0')


if __name__ == '__main__':
    port = '8080' if len(sys.argv)<2 or not sys.argv[1].isdigit() else sys.argv[1]
    run_forever(port = port)