from torpy import TorClient
import json,requests
import struct


#hostname = 'ifconfig.me'  # It's possible use onion hostname here as well
#port = 80

hostname = '128.232.229.63' #:5555'
port = 5555


#from torpy.http.requests import tor_requests_session
#with tor_requests_session() as s:



from torpy.http.requests import TorRequests
with TorRequests() as tor_requests:
    with tor_requests.get_session() as s:
    #with requests.Session() as s:
        #res = s.get('http://'+hostname+':'+str(port) + '/api/followers/MrY')
        #print(json.loads(res.text))
        res = s.get('http://'+hostname+':'+str(port))
        print(res,res.text)


# tor = TorClient()



# # # Choose random guard node and create 3-hops circuit
# # try:
# #     with tor.create_circuit(3) as circuit:
# #         # Create tor stream to host    
# #         with circuit.create_stream((hostname, port)) as stream:
# #             # Now we can communicate with host
# #             stream.send(b'GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % hostname.encode())
# #             recv = stream.recv(1024 * 10)
# #             print(recv)
# # except struct.error as e:
# #     print('struct error!?',e)