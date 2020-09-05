import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade.backend.operators import *
from flask import Flask
from flask_classful import FlaskView

## Main

OPERATOR = TheOperator()


class OperatorOnPhone(FlaskView):
    def index(self):
        return OPERATOR.keychain()['pubkey']
        
    def something(self):
        return 'something'


def run_forever():
    app = Flask(__name__)
    switchboard = Switchboard()
    switchboard.register(app, route_base='/op/', route_prefix=None)
    app.run(debug=True)

if __name__ == '__main__':
    run_forever()
