"""
1-way UDP to TCP relay.

Test with netcat
1) Run TCP server:
   nc -l 999
2) Run UDP proxy:
   python udpproxy.py
3) Run UDP client:
   nc -u 127.0.0.1 8888
4) Type some strings, type enter, they should show on the TCP server
"""

import asyncio


class ProxyDatagramProtocol(asyncio.DatagramProtocol):

    def __init__(self, remote_address):
        self.remote_address = remote_address
        self.remotes = {}
        self.transport = None
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        if addr in self.remotes:
            self.remotes[addr].transport.write(data)
            return
        loop = asyncio.get_event_loop()
        self.remotes[addr] = RemoteStreamProtocol(self, data)
        coro = loop.create_connection(
            lambda: self.remotes[addr], host=self.remote_address[0], port=int(self.remote_address[1]))
        asyncio.ensure_future(coro)


class RemoteStreamProtocol(asyncio.Protocol):

    def __init__(self, proxy, data):
        self.proxy = proxy
        self.data = data
        self.transport = None
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        self.transport.write(self.data)

    def data_received(self, data, _):
        pass

    def eof_received(self):
        pass


def start_datagram_proxy(bind, port, remote_host, remote_port):
    loop = asyncio.get_event_loop()
    protocol = ProxyDatagramProtocol((remote_host, remote_port))
    return (yield from loop.create_datagram_endpoint(lambda: protocol, local_addr=(bind, port)))


def main(bind='0.0.0.0', port=8888, remote_host='127.0.0.1', remote_port=9999):
    loop = asyncio.get_event_loop()
    print("Starting datagram proxy...")
    coro = start_datagram_proxy(bind, port, remote_host, remote_port)
    transport, _ = loop.run_until_complete(coro)
    print("Datagram proxy is running on " + str(port))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    print("Closing transport...")
    transport.close()
    loop.close()


if __name__ == '__main__':
    main()