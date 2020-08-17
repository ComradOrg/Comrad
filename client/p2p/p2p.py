import logging
import asyncio

from kademlia.network import Server
from kademlia.storage import *
import shelve
from collections import OrderedDict
import pickle,os

NODES_PRIME = [("128.232.229.63",8468), ("68.66.241.111",8468)]    


class HalfForgetfulStorage(ForgetfulStorage):
    def __init__(self, ttl=604800):
        """
        By default, max age is a week.
        """
        self.fn='sto.dat'
        if not os.path.exists(self.fn):
            self.data={}
        else:
            with open(self.fn,'rb') as f:
                self.data=pickle.load(f)


        print('loaded:',self.data)

        #self.data = pickle.open('sto.dat','rb') #,writeback=True)
        # self.data = self.store.get('OrderedDict',OrderedDict())
        self.ttl = ttl

    def __setitem__(self, key, value):
        self.data[key] = (time.monotonic(), value)
        self.write()

    def set(key,value):
        self[key]=value

    def write(self):
        with open(self.fn,'wb') as f:
            pickle.dump(self.data, f)

    def get(self, key, default=None):
        # self.cull()
        print('looking for key: ', key)
        if key in self.data:
            print('found it!')
            return self[key]
        return default

    def __getitem__(self, key):
        return self.data[key][1]




def start_first_node():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)


    shelf = HalfForgetfulStorage()

    server = Server(storage=shelf)
    loop.run_until_complete(server.listen(8468))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()


def connect():
    # host="0.0.0.0"

    async def run():
        # Create a node and start listening on port 5678
        node = Server(storage=HalfForgetfulStorage())
        await node.listen(8469)

        # Bootstrap the node by connecting to other known nodes, in this case
        # replace 123.123.123.123 with the IP of another node and optionally
        # give as many ip/port combos as you can for other nodes.
        await node.bootstrap(NODES_PRIME)

        # set a value for the key "my-key" on the network
        #await node.set("my-key2", "my awesome value")

        # get the value associated with "my-key" from the network
        #result = await node.get("my-key2")
        # print(result)
        return node

    return asyncio.run(run())
