import logging
import asyncio


import shelve
from collections import OrderedDict
import pickle,os

NODES_PRIME = [("128.232.229.63",8468), ("68.66.241.111",8468)]    

def start_udp_tcp_bridge():
    from twisted.internet.protocol import Protocol, Factory, DatagramProtocol
    from twisted.internet import reactor

    class TCPServer(Protocol):
        def connectionMade(self):
            self.port = reactor.listenUDP(8000, UDPServer(self))

        def connectionLost(self, reason):
            self.port.stopListening()

    


    # class UDPServer(DatagramProtocol):
    #     def __init__(self, stream):
    #         self.stream = stream

    #     def datagramReceived(self, datagram, address):
    #         self.stream.transport.write(datagram)

async def tcp_echo_client(message):
    
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    for n in range(5):
        print(f'Send: {message!r}')
        writer.write(message.encode())
        await writer.drain()
        import time
        await asyncio.sleep(1)

        #data = await reader.read(100)
        #print(f'Received: {data.decode()!r}')

        #asyncio.sleep(1)
    
    print('Close the connection')
    #writer.close()
    #await writer.wait_closed()

async def echo(msg):
    print('echo',msg)    

def boot_selfless_node(port=8468):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.INFO)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    # loop.create_task(tcp_echo_client('hello'))
    # loop.create_task(echo('hello??'))

    # ## UDP <-> TCP bridge
    # print("Starting datagram proxy...")
    # coro = start_datagram_proxy(bind, port, remote_host, remote_port)
    # transport, _ = loop.run_until_complete(coro)
    # print("Datagram proxy is running on " + str(port))
   



    # shelf = HalfForgetfulStorage()
    shelf = None
    print('starting kad server')

    #server = Server(storage=shelf)
    from kad import KadServer,HalfForgetfulStorage
    server = KadServer(storage=HalfForgetfulStorage())
    loop.run_until_complete(server.listen(port))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()

def start_second_node(port=8467):
    start_first_node(port=port)

# def connect():
#     # host="0.0.0.0"

#     async def run():
#         # Create a node and start listening on port 5678
#         node = Server(storage=HalfForgetfulStorage())
#         await node.listen(8469)

#         # Bootstrap the node by connecting to other known nodes, in this case
#         # replace 123.123.123.123 with the IP of another node and optionally
#         # give as many ip/port combos as you can for other nodes.
#         await node.bootstrap(NODES_PRIME)

#         # set a value for the key "my-key" on the network
#         #await node.set("my-key2", "my awesome value")

#         # get the value associated with "my-key" from the network
#         #result = await node.get("my-key2")
#         # print(result)
#         return node

#     return asyncio.run(run())
