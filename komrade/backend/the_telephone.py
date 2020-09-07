# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *

### ACTUAL PHONE CONNECTIONS
class TheTelephone(Operator):
    """
    API client class for Caller to interact with The Operator.
    """
    def __init__(self, caller=None):
        global OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN
        print('OP???',OPERATOR_KEYCHAIN)
        print('PH???',TELEPHONE_KEYCHAIN)
        
        super().__init__(
            name=TELEPHONE_NAME,
            path_crypt_keys=PATH_CRYPT_CA_KEYS,
            path_crypt_data=PATH_CRYPT_CA_KEYS
        )
        
        if not TELEPHONE_KEYCHAIN or not OPERATOR_KEYCHAIN:
            OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN = connect_phonelines()
        
        print('OP2???',OPERATOR_KEYCHAIN)
        print('PH2???',TELEPHONE_KEYCHAIN)
        
        self.caller=caller
        self._keychain = TELEPHONE_KEYCHAIN
        print(type(self._keychain), self._keychain)
        

    def send_and_receive(self,msg):
        self.log(msg,'msg!?')
        msg_b64=b64encode(msg)
        
        self.log(msg_b64,'msg_b64!?')

        msg_b64_str = msg_b64.decode()
        self.log(msg_b64_str,'msg_b64_str!?')

        msg=msg_b64_str.replace('/','_')
        URL = OPERATOR_API_URL + msg + '/'
        self.log("DIALING THE OPERATOR:",URL)
        # stop
        r=komrade_request(URL)
        if r.status_code==200:
            return r.text
        else:
            self.log('!! error in request',r.status_code,r.text)
            return None
        
    def recv(self,data):
        # decrypt
        data_in = self.decrypt_incoming(data)
        # route
        result = self.route(data_json)
        # encrypt
        data_out = self.encrypt_outgoing(result)
        # send
        return self.send(res)


    def ring_operator(self,
            from_caller=None,
            to_caller=None,
            json_phone2phone={}, 
            json_caller2phone={},   # (person) -> operator or operator -> (person)
            json_caller2caller={}):
        
        encr_msg_to_send = self.ring_ring(
            from_phone=self,
            to_phone=self.op,
            from_caller=from_caller,
            to_caller=to_caller,
            json_phone2phone=json_caller2phone, 
            json_caller2phone=json_caller2phone,   # (person) -> operator
            json_caller2caller=json_caller2caller)

        self.send_and_receive(encr_msg_to_send)
        


    
def test_call():
    caller = Caller('marx33') #Caller('marx')
    # caller.boot(create=True)
    # print(caller.keychain())
    # phone = TheTelephone()
    # req_json = {'_route':'forge_new_keys','name':name, 'pubkey_is_public':pubkey_is_public}}
    # req_json_s = jsonify(req_json)
    # res = phone.req({'forge_new_keys':{'name':'marx', 'pubkey_is_public':True}})
    # print(res)
    # asyncio.run(caller.get_new_keys())
    x=caller.get_new_keys()

    print('YEAH COOL',x)

## main
if __name__=='__main__': test_call()