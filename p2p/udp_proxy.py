import socket
from threading import Thread

class Proxy(Thread):
    """ used to proxy single udp connection
    """
    BUFFER_SIZE = 4096
    def __init__(self, listening_address, forward_address):
    	print " Server started on", listening_address
    	Thread.__init__(self)
    	self.bind = listening_address
    	self.target = forward_address

    def run(self):
    	# listen for incoming connections:
    	target = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    	target.connect(self.target)

    	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    	try:
    		s.bind(self.bind)
    	except socket.error, err:
    		print "Couldn't bind server on %r" % (self.bind, )
    		raise SystemExit
    	while 1:
    		datagram = s.recv(self.BUFFER_SIZE)
    		if not datagram:
    			break
    		length = len(datagram)
    		sent = target.send(datagram)
    		if length != sent:
    			print 'cannot send to %r, %r !+ %r' % (self.target, length, sent)
    	s.close()


if __name__ == "__main__":
    LISTEN = ("0.0.0.0", 53)
    TARGET = ("172.30.14.11", 53)
    while 1:
    	proxy = Proxy(LISTEN, TARGET)
    	proxy.start()
    	proxy.join()
    	print ' [restarting] '