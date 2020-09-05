log=print

def get_tor_python_session():
    # from torpy.http.requests import TorRequests
    # with TorRequests() as tor_requests:
    #     with tor_requests.get_session() as s:
    # #         return s
    # from torpy.http.requests import tor_requests_session
    # with tor_requests_session() as s:  # returns requests.Session() object
    #     return s
    pass

        

def get_tor_proxy_session():
    import requests
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




def tor_request(url,method='get',data=None):
    with get_tor_proxy_session() as s:
        if method=='get':
            return s.get(url)
        elif method=='post':
            log('data',data)
            return s.post(url,data=data)


def request(Q,**kwargs):
    log('request() Q:',Q)
    res = tor_request(Q,**kwargs)
    log('reqeust() <-',res)
    return res
    

