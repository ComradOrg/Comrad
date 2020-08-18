import logging
import asyncio


import shelve
from collections import OrderedDict
import pickle,os

NODES_PRIME = [("128.232.229.63",8468), ("68.66.241.111",8468)]    




def start_first_node(port=8468):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.INFO)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)


    # shelf = HalfForgetfulStorage()
    shelf = None

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
