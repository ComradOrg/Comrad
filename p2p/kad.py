###
# Kademlia patches
###

from kademlia.storage import *
from kademlia.network import *
from kademlia.routing import RoutingTable
from rpcudp.protocol import RPCProtocol
import os


PROXY_ADDR = ('0.0.0.0',1194)

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


        #print('>> loaded %s keys' % len(self.data))

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





"""UDP proxy server."""

import asyncio


class ProxyDatagramProtocol(asyncio.DatagramProtocol):

    def __init__(self, remote_address=PROXY_ADDR):
        self.remote_address = remote_address
        self.remotes_d = {}
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        if addr in self.remotes_d:
            self.remotes_d[addr].transport.sendto(data)
            return
        loop = asyncio.get_event_loop()
        self.remotes_d[addr] = RemoteDatagramProtocol(self, addr, data)
        coro = loop.create_datagram_endpoint(
            lambda: self.remotes_d[addr], remote_addr=self.remote_address)
        asyncio.ensure_future(coro)


class RemoteDatagramProtocol(asyncio.DatagramProtocol):

    def __init__(self, proxy, addr, data):
        print('RemoteDP got:',proxy,addr,data)
        self.proxy = proxy
        self.addr = addr
        self.data = data
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(self.data)

    def datagram_received(self, data, _):
        self.proxy.transport.sendto(data, self.addr)

    def connection_lost(self, exc):
        self.proxy.remotes.pop(self.attr)


async def start_datagram_proxy(protocol_class, bind, port, remote_host, remote_port):
    loop = asyncio.get_event_loop()
    protocol = protocol_class((remote_host, remote_port))
    return await loop.create_datagram_endpoint(
        lambda: protocol, local_addr=(bind, port))


def main(bind='0.0.0.0', port=8888,
        remote_host='0.0.0.0', remote_port=9999):
    loop = asyncio.get_event_loop()
    print("Starting datagram proxy...")
    coro = start_datagram_proxy(bind, port, remote_host, remote_port)
    transport, _ = loop.run_until_complete(coro)
    print("Datagram proxy is running...")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    print("Closing transport...")
    transport.close()
    loop.close()


if __name__ == '__main__':
    main()



# class KadProtocol(RPCProtocol, ProxyDatagramProtocol):
#     def __init__(self, source_node, storage, ksize):
#         ProxyDatagramProtocol.__init__(self)
#         RPCProtocol.__init__(self)
        
#         self.router = RoutingTable(self, ksize, source_node)
#         self.storage = storage
#         self.source_node = source_node



class KadProtocol(KademliaProtocol):
    # def datagram_received(self, data, addr):
    #     LOG.debug("received datagram from %s", addr)
    #     asyncio.ensure_future(self._solve_datagram(data, addr))
    remote_address = PROXY_ADDR
    REMOTES_D={}

    def datagram_received(self, data, addr):
        #if not hasattr(self,'remotes_d'): self.remotes_d={}
        # print('\n\n!?!?!?',self.REMOTES_D, type(self.REMOTES_D))
        # if addr in self.REMOTES_D:
        #     self.REMOTES_D[addr].transport.sendto(data)
        #     return
        loop = asyncio.get_event_loop()
        # self.REMOTES_D[addr] = RemoteDatagramProtocol(self, addr, data)
        RDP = RemoteDatagramProtocol(self, addr, data)
        coro = loop.create_datagram_endpoint(lambda: RDP, remote_addr=self.remote_address)
        asyncio.ensure_future(coro)

# async def start_datagram_proxy2(protocol_class, bind, port, remote_host, remote_port, source_node, storage, ksize):
#     loop = asyncio.get_event_loop()
#     protocol = protocol_class(source_node, storage, ksize)
#     return await loop.create_datagram_endpoint(
#         lambda: protocol, local_addr=(bind, port))

class KadServer(Server):
    protocol_class = KademliaProtocol

    # async def listen(self, port, interface='0.0.0.0'):
    #     """
    #     Start listening on the given port.

    #     Provide interface="::" to accept ipv6 address
    #     """
    #     loop = asyncio.get_event_loop()

    #     remote_host='0.0.0.0'
    #     remote_port=123

    #     #listen = start_datagram_proxy2(self.protocol_class, interface, port, remote_host, remote_port, self.node, self.storage, self.ksize)
    
    #     listen = loop.create_datagram_endpoint(self._create_protocol,
    #                                            local_addr=(interface, port))
    #     log.info("Node %i listening on %s:%i",
    #              self.node.long_id, interface, port)
    #     self.transport, self.protocol = await listen
    #     # finally, schedule refreshing table
    #     self.refresh_table()
    
    pass






### FOR REFERENCE:
class RPCProtocol(asyncio.DatagramProtocol):
    """
    Protocol implementation using msgpack to encode messages and asyncio
    to handle async sending / recieving.
    """
    def __init__(self, wait_timeout=5):
        """
        Create a protocol instance.
        Args:
            wait_timeout (int): Time to wait for a response before giving up
        """
        self._wait_timeout = wait_timeout
        self._outstanding = {}
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        LOG.debug("received datagram from %s", addr)
        asyncio.ensure_future(self._solve_datagram(data, addr))

    async def _solve_datagram(self, datagram, address):
        if len(datagram) < 22:
            LOG.warning("received datagram too small from %s,"
                        " ignoring", address)
            return

        msg_id = datagram[1:21]
        data = umsgpack.unpackb(datagram[21:])

        if datagram[:1] == b'\x00':
            # schedule accepting request and returning the result
            asyncio.ensure_future(self._accept_request(msg_id, data, address))
        elif datagram[:1] == b'\x01':
            self._accept_response(msg_id, data, address)
        else:
            # otherwise, don't know the format, don't do anything
            LOG.debug("Received unknown message from %s, ignoring", address)

    def _accept_response(self, msg_id, data, address):
        msgargs = (b64encode(msg_id), address)
        if msg_id not in self._outstanding:
            LOG.warning("received unknown message %s "
                        "from %s; ignoring", *msgargs)
            return
        LOG.debug("received response %s for message "
                  "id %s from %s", data, *msgargs)
        future, timeout = self._outstanding[msg_id]
        timeout.cancel()
        future.set_result((True, data))
        del self._outstanding[msg_id]

    async def _accept_request(self, msg_id, data, address):
        if not isinstance(data, list) or len(data) != 2:
            raise MalformedMessage("Could not read packet: %s" % data)
        funcname, args = data
        func = getattr(self, "rpc_%s" % funcname, None)
        if func is None or not callable(func):
            msgargs = (self.__class__.__name__, funcname)
            LOG.warning("%s has no callable method "
                        "rpc_%s; ignoring request", *msgargs)
            return

        if not asyncio.iscoroutinefunction(func):
            func = asyncio.coroutine(func)
        response = await func(address, *args)
        LOG.debug("sending response %s for msg id %s to %s",
                  response, b64encode(msg_id), address)
        txdata = b'\x01' + msg_id + umsgpack.packb(response)
        self.transport.sendto(txdata, address)

    def _timeout(self, msg_id):
        args = (b64encode(msg_id), self._wait_timeout)
        LOG.error("Did not receive reply for msg "
                  "id %s within %i seconds", *args)
        self._outstanding[msg_id][0].set_result((False, None))
        del self._outstanding[msg_id]

    def __getattr__(self, name):
        """
        If name begins with "_" or "rpc_", returns the value of
        the attribute in question as normal.
        Otherwise, returns the value as normal *if* the attribute
        exists, but does *not* raise AttributeError if it doesn't.
        Instead, returns a closure, func, which takes an argument
        "address" and additional arbitrary args (but not kwargs).
        func attempts to call a remote method "rpc_{name}",
        passing those args, on a node reachable at address.
        """
        if name.startswith("_") or name.startswith("rpc_"):
            return getattr(super(), name)

        try:
            return getattr(super(), name)
        except AttributeError:
            pass

        def func(address, *args):
            msg_id = sha1(os.urandom(32)).digest()
            data = umsgpack.packb([name, args])
            if len(data) > 8192:
                raise MalformedMessage("Total length of function "
                                       "name and arguments cannot exceed 8K")
            txdata = b'\x00' + msg_id + data
            LOG.debug("calling remote function %s on %s (msgid %s)",
                      name, address, b64encode(msg_id))
            self.transport.sendto(txdata, address)

            loop = asyncio.get_event_loop()
            if hasattr(loop, 'create_future'):
                future = loop.create_future()
            else:
                future = asyncio.Future()
            timeout = loop.call_later(self._wait_timeout,
                                      self._timeout, msg_id)
            self._outstanding[msg_id] = (future, timeout)
            return future

        return func