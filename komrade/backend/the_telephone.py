# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
from komrade.backend.phonelines import *

### ACTUAL PHONE CONNECTIONS
class TheTelephone(Operator):
    """
    API client class for Caller to interact with The Operator.
    """
    def __init__(self, caller=None):
        super().__init__(name=TELEPHONE_NAME)
        self.caller=caller
        self._keychain = self.telephone_keychain

    def find_pubkey(self):
        return self.telephone_keychain.get('pubkey')

    def send_and_receive(self,msg):
        msg_b64_str = b64encode(msg).decode()
        msg_b64_str_esc = msg_b64_str.replace('/','_')
        self.log('msg_b64_str_esc',type(msg_b64_str_esc),msg_b64_str_esc)
        URL = OPERATOR_API_URL + msg_b64_str_esc + '/'
        self.log("DIALING THE OPERATOR:",URL)
        ringring=komrade_request(URL)
        if ringring.status_code==200:
            # response back from Operator!
            encr_str_response_from_op = ringring.text
            self.log('encr_str_response_from_op',encr_str_response_from_op)
            return encr_str_response_from_op #.encode()
        else:
            self.log('!! error in request',ringring.status_code,ringring.text)
            return None

    def ring_ring(self,msg):
        return super().ring_ring(
            msg,
            to_whom=self.op,
            get_resp_from=self.send_and_receive
        )
        
    
def test_call():
    phone = TheTelephone()
    pprint(phone.keychain())


    # caller = Caller('marx33') #Caller('marx')
    # caller.boot(create=True)
    # print(caller.keychain())
    # phone = TheTelephone()
    # req_json = {'_please':'forge_new_keys','name':name, 'pubkey_is_public':pubkey_is_public}}
    # req_json_s = jsonify(req_json)
    # res = phone.req({'forge_new_keys':{'name':'marx', 'pubkey_is_public':True}})
    # print(res)
    # asyncio.run(caller.get_new_keys())
    # x=caller.get_new_keys(passphrase='1869')

    # print('YEAH COOL',x)

## main
if __name__=='__main__': test_call()