# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from comrad import *
from comrad.backend import *
from comrad.backend.phonelines import *
from comrad.backend.operators import CALLBACKS
import requests
from torpy.cell_socket import TorSocketConnectError
from requests.exceptions import ConnectionError

# def TheTelephone(*x,**y):
#     return Comrad(TELEPHONE_NAME,*x,**y)

### ACTUAL PHONE CONNECTIONS
class TheTelephone(Operator):
    """
    API client class for Caller to interact with The Operator.
    """
    def __init__(self, caller=None, callbacks={}):
        super().__init__(name=TELEPHONE_NAME,callbacks=callbacks)
        self.caller=caller
        from comrad.backend.phonelines import check_phonelines
        keychain = check_phonelines()[TELEPHONE_NAME]
        self._keychain ={**self.load_keychain_from_bytes(keychain)}

        self.log(f'Starting up with callbacks: {self._callbacks}')


    @property
    def api_url(self):
        #if 'COMRAD_OPERATOR_API_URL' in os.environ and os.environ['COMRAD_OPERATOR_API_URL']:
        #    return os.environ
        #os.environ['COMRAD_OPERATOR_API_URL'] = OPERATOR_API_URL_TOR
        if 'COMRAD_USE_TOR' in os.environ and os.environ['COMRAD_USE_TOR']=='1':
            return OPERATOR_API_URL_TOR
        elif 'COMRAD_USE_CLEARNET' in os.environ and os.environ['COMRAD_USE_CLEARNET']=='1':
            return OPERATOR_API_URL_CLEARNET
        else:
            return OPERATOR_API_URL


    async def send_and_receive(self,msg_d,n_attempts=3,**y):
        # self.log('send and receive got incoming msg:',msg_d)
        
        # assert that people can speak only with operator in their first enclosed message!
        # if so, dropping the "to"
        if msg_d['to'] != self.op.pubkey.data:
            raise ComradException('Comrades must communicate securely with Operator first.')
        # opp = Operator(pubkey=msg_d['to'])
        # self.log('got opp:',opp.pubkey.data == msg_d['to'], self.op.pubkey.data == msg_d['to'])

        # self.log('got msg_d:',msg_d)

        # self.log('but going to send just msg?',msg_b)
        
        msg_b=msg_d["msg"]
        msg_b64 = b64encode(msg_b)
        msg_b64_str = msg_b64.decode()
        self.log(f'''Sending the encrypted content package:\n\n{msg_b64_str}''')

        # seal for transport
        msg_b64_str_esc = msg_b64_str.replace('/','_')

        # dial the operator
        


        URL = self.api_url + msg_b64_str_esc + '/'
        self.log("DIALING THE OPERATOR:",URL)

        # phonecall=await self.comrad_request_async(URL)
        # import asyncio
        # loop = asyncio.get_event_loop()
        texec = ThreadExecutor()

        
        for n_attempt in range(n_attempts):
            self.log('making first attempt to connect via Tor')
            try:
                # phonecall=self.comrad_request(URL)
                phonecall = await texec(self.comrad_request, URL)
                break
            except (TorSocketConnectError,ConnectionError) as e:
                self.log(f'!! {e} trying again?')
                pass

        if phonecall.status_code!=200:
            self.log('!! error in request',phonecall.status_code,phonecall.text)
            return
        
        # response back from Operator!
        resp_msg_b64_str = phonecall.text
        self.log(f'{self}: Received response from Operator! We got back:\n\n',resp_msg_b64_str)

        resp_msg_b64 = resp_msg_b64_str.encode()
        resp_msg_b = b64decode(resp_msg_b64)
        # self.log('resp_msg_b:',resp_msg_b)
        resp_msg_d = pickle.loads(resp_msg_b)
        # self.log('unpickled:',resp_msg_d)

        # unseal
        from comrad.backend.messages import Message
        resp_msg_obj = Message(resp_msg_d)
        # res =  resp_msg_b_unsealed
        # self.log('Decoding binary, message discovered:\n',resp_msg_obj)

        # decrypt
        # resp_msg_obj.decrypt()
        # self.log('returning decrypted form:',resp_msg_obj)

        return resp_msg_obj
        # return self.pronto_pronto(resp_msg_obj)


    async def ring_ring(self,msg,**y):
        return await super().ring_ring(
            msg,
            to_whom=self.op,
            get_resp_from=self.send_and_receive,
            **y
        )

    ### Requests functionality
    def comrad_request(self,url,allow_clearnet = ALLOW_CLEARNET):
        if '.onion' in url or not allow_clearnet:
            return self.tor_request(url)
        return requests.get(url,timeout=60)

    async def comrad_request_async(self,url,allow_clearnet=ALLOW_CLEARNET):
        import requests_async as requests
        if '.onion' in url or not allow_clearnet:
            return await self.tor_request_async(url)
        return await requests.get(url,timeout=60)


    def tor_request(self,url):
        return self.tor_request_in_python(url)
        # return tor_request_in_proxy(url)

    async def tor_request_async(self,url):
        return await self.tor_request_in_python_async(url)
        

    def tor_request_in_proxy(self,url):
        with self.get_tor_proxy_session() as s:
            return s.get(url,timeout=600)

    async def tor_request_in_python_async(self,url):
        import requests_async
        tor = TorClient()
        with tor.get_guard() as guard:
            adapter = TorHttpAdapter(guard, 3, retries=RETRIES)

            async with requests_async.Session() as s:
                s.headers.update({'User-Agent': 'Mozilla/5.0'})
                s.mount('http://', adapter)
                s.mount('https://', adapter)
                r = s.get(url, timeout=600)
                self.log('<-- r',r)
                return r


    def tor_request_in_python(self,url):
        tor = TorClient()
        with tor.get_guard() as guard:
            adapter = TorHttpAdapter(guard, 3, retries=RETRIES)

            with requests.Session() as s:
                s.headers.update({'User-Agent': 'Mozilla/5.0'})
                s.mount('http://', adapter)
                s.mount('https://', adapter)
                r = s.get(url, timeout=600)
                return r

    def get_tor_proxy_session(self):
        session = requests.session()
        # Tor uses the 9050 port as the default socks port
        session.proxies = {'http':  'socks5://127.0.0.1:9050',
                        'https': 'socks5://127.0.0.1:9050'}
        return session    

    def get_async_tor_proxy_session(self):
        import requests_futures
        from requests_futures.sessions import FuturesSession
        session = FuturesSession()
        # Tor uses the 9050 port as the default socks port
        session.proxies = {'http':  'socks5://127.0.0.1:9050',
                        'https': 'socks5://127.0.0.1:9050'}
        return session    
















        
    
def test_call():
    phone = TheTelephone()

    pprint(phone.keychain())
    

    # caller = Caller('marx33') #Caller('marx')
    # caller.boot(create=True)
    # print(caller.keychain())
    # phone = TheTelephone()
    # req_json = {'_route':'forge_new_keys','name':name, 'pubkey_is_public':pubkey_is_public}}
    # req_json_s = jsonify(req_json)
    # res = phone.req({'forge_new_keys':{'name':'marx', 'pubkey_is_public':True}})
    # print(res)
    # asyncio.run(caller.get_new_keys())
    # x=caller.get_new_keys(passphrase='1869')

    # print('YEAH COOL',x)

## main
if __name__=='__main__': test_call()