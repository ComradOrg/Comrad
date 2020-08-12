from gevent.pywsgi import WSGIServer
from server import app

http_server = WSGIServer(('', 5555), app)
http_server.serve_forever()