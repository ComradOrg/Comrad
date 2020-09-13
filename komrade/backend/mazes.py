import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
# import requests_async as requests

log=print

def komrade_request(url,allow_clearnet = ALLOW_CLEARNET):
    if '.onion' in url or not allow_clearnet:
        return tor_request(url)
    return requests.get(url,timeout=600)

def tor_request(url):
    return tor_request_in_python(url)
    # return tor_request_in_proxy(url)

async def tor_request_async(url):
    return await tor_request_in_python_async(url)
    

def tor_request_in_proxy(url):
    with get_tor_proxy_session() as s:
        return s.get(url,timeout=60)

async def tor_request_in_python_async(url):
    import requests_async as requests
    tor = TorClient()
    with tor.get_guard() as guard:
        adapter = TorHttpAdapter(guard, 3, retries=RETRIES)

        async with requests.Session() as s:
            # await s
            s.headers.update({'User-Agent': 'Mozilla/5.0'})
            s.mount('http://', adapter)
            s.mount('https://', adapter)
            return await s.get(url, timeout=60)


def tor_request_in_python(url):
    tor = TorClient()
    with tor.get_guard() as guard:
        adapter = TorHttpAdapter(guard, 3, retries=RETRIES)

        with requests.Session() as s:
            s.headers.update({'User-Agent': 'Mozilla/5.0'})
            s.mount('http://', adapter)
            s.mount('https://', adapter)

            # r = s.get(url, timeout=30)
            # r = s.post('http://u7spnj3dmwumzoa4.onion/op/',data=b'hello world', timeout=30)
            #_dat = 'Z29iYmxlZHlnb29rZ29iYmxlZHlnb29rZ29iYmxlZHlnb29rZ29iYmxlZHlnb29rZ29iYmxlZHlnb29rZ29iYmxlZHlnb29rZ29iYmxlZHlnb29rZ29iYmxlZHlnb29rZ29iYmxlZHlnb29r'
            r = s.get(url, timeout=60)
            
            return r
            #return r

            # #r = s.get('http://u7spnj3dmwumzoa4.onion',timeout=30)    
            # print (r, r.text[:1000])
            # return s

def get_tor_proxy_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                    'https': 'socks5://127.0.0.1:9050'}
    return session    

def get_async_tor_proxy_session():
    import requests_futures
    from requests_futures.sessions import FuturesSession
    session = FuturesSession()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                    'https': 'socks5://127.0.0.1:9050'}
    return session    




def test_torpy():
    hostname = KOMRADE_ONION
    from torpy import TorClient

    tor = TorClient()
    # Choose random guard node and create 3-hops circuit
    with tor.create_circuit(3) as circuit:
        # Create tor stream to host
        with circuit.create_stream((hostname, 80)) as stream:
            # Send some data to it
            stream.send(b'GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % hostname.encode())

            recv = recv_all(stream).decode()
            #logger.warning('recv: %s', recv)
            print('RECEIVED:',recv)






import random
def test_slow_func(n,t=1,m=10):
    for x in range(m):
        print(f'Thread #{n}: it #{x} of {m}, sleeping {m} sec..')
        yield x
        # time.sleep(t)





def test_threads():
    from multiprocessing.pool import ThreadPool
    pool = ThreadPool(processes=2)

    for x in pool.imap_unordered(test_slow_func, [1,2,3]):
        for y in x:
            print(y,'?')
        print(x,'...')


async def test_slow_func(n,t=1,m=10):
    for x in range(m):
        print(f'Thread #{n}: it #{x} of {m}, sleeping {m} sec..')
        yield x
        asyncio.sleep(t)

# test async
async def test_async():
    return await asyncio.gather(*[await test_slow_func(n) for n in range(3)])




#### CODE FROM TORPY


# Copyright 2019 James Brown
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import socket
import logging
from threading import Event
from selectors import EVENT_READ
from multiprocessing.pool import ThreadPool

import requests

from torpy import TorClient
from torpy.stream import TorStream
from torpy.utils import AuthType, recv_all, retry
from torpy.http.adapter import TorHttpAdapter
from torpy.hiddenservice import HiddenService
from torpy.http.requests import TorRequests, tor_requests_session, do_request as requests_request
from torpy.http.urlopener import do_request as urllib_request

# logging.getLogger('requests').setLevel(logging.CRITICAL)
# logging.basicConfig(format='[%(asctime)s] [%(threadName)-16s] %(message)s', level=logging.DEBUG)
# logger = logging.getLogger('komrade')


HS_BASIC_HOST = os.getenv('HS_BASIC_HOST')
HS_BASIC_AUTH = os.getenv('HS_BASIC_AUTH')

HS_STEALTH_HOST = os.getenv('HS_STEALTH_HOST')
HS_STEALTH_AUTH = os.getenv('HS_STEALTH_AUTH')

RETRIES = 3


@retry(RETRIES, (TimeoutError, ConnectionError, ))
def test_clearnet_raw():
    hostname = 'ifconfig.me'
    tor = TorClient()
    # Choose random guard node and create 3-hops circuit
    with tor.create_circuit(3) as circuit:
        # Create tor stream to host
        with circuit.create_stream((hostname, 80)) as stream:
            # Send some data to it
            stream.send(b'GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % hostname.encode())
            recv = recv_all(stream).decode()
            logger.warning('recv: %s', recv)
            search_ip = '.'.join(circuit.last_node.router.ip.split('.')[:-1]) + '.'
            assert search_ip in recv, 'wrong data received'


@retry(RETRIES, (TimeoutError, ConnectionError, ))
def test_onion_raw():
    hostname = 'u7spnj3dmwumzoa4.onion'
    tor = TorClient()
    # Choose random guard node and create 3-hops circuit
    with tor.create_circuit(3) as circuit:
        # Create tor stream to host
        with circuit.create_stream((hostname, 80)) as stream:
            # Send some data to it
            stream.send(b'GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % hostname.encode())

            recv = recv_all(stream).decode()
            logger.warning('recv: %s', recv)
            assert 'StickyNotes' in recv, 'wrong data received'


def test_requests_no_agent():
    data = requests_request('https://httpbin.org/headers', retries=RETRIES)
    assert 'User-Agent' not in data


def test_requests():
    data = requests_request('https://httpbin.org/headers', headers={'User-Agent': 'Mozilla/5.0'}, retries=RETRIES)
    assert 'Mozilla' in data


def test_requests_session():
    tor = TorClient()
    with tor.get_guard() as guard:
        adapter = TorHttpAdapter(guard, 3, retries=RETRIES)

        with requests.Session() as s:
            s.headers.update({'User-Agent': 'Mozilla/5.0'})
            s.mount('http://', adapter)
            s.mount('https://', adapter)

            r = s.get('https://google.com', timeout=30)
            logger.warning(r)
            logger.warning(r.text)
            assert r.text.rstrip().endswith('</html>')

            r = s.get('https://stackoverflow.com/questions/tagged/python')
            assert r.text.rstrip().endswith('</html>')
            logger.warning(r)
            logger.warning(r.text)

def test_requests_session2():
    tor = TorClient()
    with tor.get_guard() as guard:
        adapter = TorHttpAdapter(guard, 3, retries=RETRIES)

        with requests.Session() as s:
            s.headers.update({'User-Agent': 'Mozilla/5.0'})
            s.mount('http://', adapter)
            s.mount('https://', adapter)

            #r = s.get('https://google.com', timeout=30)
            r = s.get('http://u7spnj3dmwumzoa4.onion',timeout=30)

            print(r)
            print(r.text[:1000])

def test_urlopener_no_agent():
    data = urllib_request('https://httpbin.org/headers', verbose=1, retries=RETRIES)
    assert 'User-Agent' not in data


def test_urlopener():
    data = urllib_request('https://httpbin.org/headers', headers=[('User-Agent', 'Mozilla/5.0')], verbose=1,
                          retries=RETRIES)
    assert 'Mozilla' in data


def test_multi_threaded():
    auth_data = {HS_BASIC_HOST: (HS_BASIC_AUTH, AuthType.Basic)} if HS_BASIC_HOST and HS_BASIC_AUTH else None

    with TorRequests(auth_data=auth_data) as tor_requests:
        links = [
            'https://httpbin.org/headers',
            'https://google.com',
            'https://ifconfig.me',
            'http://facebookcorewwwi.onion',
        ]
        if HS_BASIC_HOST:
            links.append('http://' + HS_BASIC_HOST)
        links = links * 10

        with tor_requests.get_session(retries=RETRIES) as sess:

            def process(link):
                try:
                    logger.debug('get link: %s', link)
                    r = sess.get(link, timeout=30)
                    logger.warning('get link %s finish: %s', link, r)
                    return r
                except BaseException:
                    logger.exception('get link %s error', link)

            pool = ThreadPool(10)
            for i, w in enumerate(pool._pool):
                w.name = 'Worker{}'.format(i)
            results = pool.map(process, links)
            pool.close()
            pool.join()
    logger.debug('test_multi_threaded ends: %r', results)


@retry(RETRIES, (TimeoutError, ConnectionError, ))
def test_basic_auth():
    """Connecting to Hidden Service with 'Basic' authorization."""
    if not HS_BASIC_HOST or not HS_BASIC_AUTH:
        logger.warning('Skip test_basic_auth()')
        return

    hs = HiddenService(HS_BASIC_HOST, HS_BASIC_AUTH, AuthType.Basic)
    tor = TorClient()
    # Choose random guard node and create 3-hops circuit
    with tor.create_circuit(3) as circuit:
        # Create tor stream to host
        with circuit.create_stream((hs, 80)) as stream:
            # Send some data to it
            stream.send(b'GET / HTTP/1.0\r\nHost: %s.onion\r\n\r\n' % hs.onion.encode())
            recv = recv_all(stream).decode()
            logger.warning('recv: %s', recv)


@retry(RETRIES, (TimeoutError, ConnectionError, ))
def test_stealth_auth():
    """Connecting to Hidden Service with 'Stealth' authorization."""
    if not HS_STEALTH_HOST or not HS_STEALTH_AUTH:
        logger.warning('Skip test_stealth_auth()')
        return

    hs = HiddenService(HS_STEALTH_HOST, HS_STEALTH_AUTH, AuthType.Stealth)
    tor = TorClient()
    # Choose random guard node and create 3-hops circuit
    with tor.create_circuit(3) as circuit:
        # Create tor stream to host
        with circuit.create_stream((hs, 80)) as stream:
            # Send some data to it
            stream.send(b'GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % hs.hostname.encode())
            recv = recv_all(stream).decode()
            logger.warning('recv: %s', recv)


@retry(RETRIES, (TimeoutError, ConnectionError, ))
def test_basic_auth_pre():
    """Using pre-defined authorization data for making HTTP requests."""
    if not HS_BASIC_HOST or not HS_BASIC_AUTH:
        logger.warning('Skip test_basic_auth()')
        return

    hidden_service = HS_BASIC_HOST
    auth_data = {HS_BASIC_HOST: (HS_BASIC_AUTH, AuthType.Basic)}
    tor = TorClient(auth_data=auth_data)
    # Choose random guard node and create 3-hops circuit
    with tor.create_circuit(3) as circuit:
        # Create tor stream to host
        with circuit.create_stream((hidden_service, 80)) as stream:
            # Send some data to it
            stream.send(b'GET / HTTP/1.0\r\nHost: %s.onion\r\n\r\n' % hidden_service.encode())
            recv = recv_all(stream).decode()
            logger.warning('recv: %s', recv)


def test_requests_hidden():
    """Using pre-defined authorization data for making HTTP requests by tor_requests_session."""
    if not HS_BASIC_HOST or not HS_BASIC_AUTH:
        logger.warning('Skip test_requests_hidden()')
        return

    auth_data = {HS_BASIC_HOST: (HS_BASIC_AUTH, AuthType.Basic)}
    with tor_requests_session(auth_data=auth_data, retries=RETRIES) as sess:
        r = sess.get('http://{}/'.format(HS_BASIC_HOST), timeout=30)
        logger.warning(r)
        logger.warning(r.text)


@retry(2, (TimeoutError, ConnectionError, ))
def test_select():
    sock_r, sock_w = socket.socketpair()

    events = {TorStream: {'data': Event(), 'close': Event()},
              socket.socket: {'data': Event(), 'close': Event()}}

    hostname = 'ifconfig.me'
    tor = TorClient()
    with tor.get_guard() as guard:

        def recv_callback(sock_or_stream, mask):
            logger.debug(f'recv_callback {sock_or_stream}')
            kind = type(sock_or_stream)
            data = sock_or_stream.recv(1024)
            logger.info('%s: %r', kind.__name__, data.decode())
            if data:
                events[kind]['data'].set()
            else:
                logger.debug('closing')
                guard.unregister(sock_or_stream)
                events[kind]['close'].set()

        with guard.create_circuit(3) as circuit:
            with circuit.create_stream((hostname, 80)) as stream:
                guard.register(sock_r, EVENT_READ, recv_callback)
                guard.register(stream, EVENT_READ, recv_callback)

                stream.send(b'GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % hostname.encode())
                sock_w.send(b'some data')

                assert events[socket.socket]['data'].wait(10), 'no sock data received'
                assert events[TorStream]['data'].wait(30), 'no stream data received'

                sock_w.close()
                assert events[socket.socket]['close'].wait(10), 'no sock close received'
                assert events[TorStream]['close'].wait(10), 'no stream close received'




























if __name__=='__main__':
    test_torpy()