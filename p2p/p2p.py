import logging
import asyncio


import shelve
from collections import OrderedDict
import pickle,os

# NODES_PRIME = [("128.232.229.63",8467), ("68.66.241.111",8467)]    

NODES_PRIME = [("68.66.241.111",8467)] #    ("10.42.0.13",8467)]

async def echo(msg):
    print('echo',msg)    

# def boot_selfless_node(port=8468, loop=None):
#     # handler = logging.StreamHandler()
#     # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     # handler.setFormatter(formatter)
#     # log = logging.getLogger('kademlia')
#     # log.addHandler(handler)
#     # log.setLevel(logging.DEBUG)

#     if not loop: loop = asyncio.get_event_loop()
#     loop.set_debug(True)

#     # shelf = HalfForgetfulStorage()

#     #server = Server(storage=shelf)
#     try:
#         from kad import KadServer,HalfForgetfulStorage
#     except ImportError:
#         from .kad import KadServer,HalfForgetfulStorage
    
#     server = KadServer(storage=HalfForgetfulStorage())
#     loop.create_task(server.listen(port))

#     # try:
#     #     loop.run_forever()
#     # except KeyboardInterrupt:
#     #     pass
#     # finally:
#     #     server.stop()
#     #     loop.close()
#     return server,loop


def boot_lonely_selfless_node(port=8467):
    # handler = logging.StreamHandler()
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    # log = logging.getLogger('kademlia')
    # log.addHandler(handler)
    # log.setLevel(logging.DEBUG)

    # import asyncio
    # loop = asyncio.new_event_loop()

    # # async def go():
    # #     from api import _getdb
    # #     node = await _getdb()
    # #     i=0
    # #     while i+1:
    # #         if not i%10: print(node)
    # #         await asyncio.sleep(5)
    # #         i+=1

    
    
    # asyncio.run(go())
    async def go():
        from api import Api,PORT_LISTEN
        API = Api()
        await API.connect_forever(8467)
    asyncio.run(go())
    
