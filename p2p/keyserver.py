# using https://github.com/lals1/python-keyserver

# """
# Run primitive keyserver
# Only on node prime!
# """
# import os
# from flask import Flask

# keyhome = os.path.join(os.path.expanduser('~'),'.komrade','.keyserver')
# if not os.path.exists(keyhome): os.makedirs(keyhome)

# keyserver = 'komrade.app'
# keyserver_port = 5566

# app = Flask(__name__)

# storage = '.keyring'

# @app.route('/')
# def hello():
#     return "Hello World!"

# @app.route('/add/<name>/key')
# def add(name,key):
#     #return "Hello {}!".format(name)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0',port=keyserver_port)