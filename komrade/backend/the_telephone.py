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
        from komrade.backend.phonelines import check_phonelines
        keychain = check_phonelines()[TELEPHONE_NAME]
        self._keychain = self.load_keychain_from_bytes(keychain)


    def send_and_receive(self,msg_d,**y):
        # self.log('send and receive got incoming msg:',msg_d)
        
        # assert that people can speak only with operator in their first enclosed message!
        # if so, dropping the "to"
        if msg_d['to'] != self.op.pubkey.data:
            raise KomradeException('Komrades must communicate securely with Operator first.')
        # opp = Operator(pubkey=msg_d['to'])
        # self.log('got opp:',opp.pubkey.data == msg_d['to'], self.op.pubkey.data == msg_d['to'])
        
        msg_b=msg_d["msg"]
        msg_b64 = b64encode(msg_b)
        msg_b64_str = msg_b64.decode()
        self.log(f'''Sending the encrypted content package:\n\n{msg_b64_str}''')

        # seal for transport
        msg_b64_str_esc = msg_b64_str.replace('/','_')

        # dial the operator
        URL = OPERATOR_API_URL + msg_b64_str_esc + '/'
        self.log("DIALING THE OPERATOR:",URL)
        phonecall=komrade_request(URL)
        if phonecall.status_code!=200:
            self.log('!! error in request',phonecall.status_code,phonecall.text)
            return
        
        # response back from Operator!
        resp_msg_b64_str = phonecall.text
        # self.log('resp_msg_b64_str',resp_msg_b64_str)

        resp_msg_b64 = resp_msg_b64_str.encode()
        resp_msg_b = b64decode(resp_msg_b64)

        # unseal
        resp_msg_obj = self.unseal_msg(resp_msg_b)
        # res =  resp_msg_b_unsealed
        self.log('unsealed resp_msg_obj',resp_msg_obj)

        # decrypt
        # resp_msg_obj.decrypt()
        # self.log('returning decrypted form:',resp_msg_obj)

        return resp_msg_obj
        # return self.pronto_pronto(resp_msg_obj)


    def ring_ring(self,msg,**y):
        return super().ring_ring(
            msg,
            to_whom=self.op,
            get_resp_from=self.send_and_receive,
            **y
        )
        
    
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