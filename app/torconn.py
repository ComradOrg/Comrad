from torpy import TorClient
import json,requests
import struct


#hostname = 'ifconfig.me'  # It's possible use onion hostname here as well
#port = 80

#hostname = 'komrades.net'
hostname = '128.232.229.63'
port = 5555


def try_torpy():
    from torpy.http.requests import TorRequests
    with TorRequests() as tor_requests:
        with tor_requests.get_session() as s:
        #with requests.Session() as s:
            #res = s.get('http://'+hostname+':'+str(port) + '/api/followers/MrY')
            #print(json.loads(res.text))
            res = s.get('http://'+hostname+':'+str(port))
            print(res,res.text)



def try_proxy():
    import requests

    def get_tor_session():
        session = requests.session()
        # Tor uses the 9050 port as the default socks port
        session.proxies = {'http':  'socks5://127.0.0.1:9050',
                        'https': 'socks5://127.0.0.1:9050'}
        return session

    # Make a request through the Tor connection
    # IP visible through Tor
    session = get_tor_session()
    print(session.get("http://"+hostname+':'+str(port)).text)
    # Above should print an IP different than your public IP

    # Following prints your normal public IP
    print(session.get("http://ifconfig.me").text)



try_proxy()
#try_torpy()