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


    # async def req(self,json_phone={},json_caller={},caller=None):
    def ask_operator(self,
                    json_phone2op={},
                    json_caller2op={},
                    json_caller2caller={},from_caller=None,to_caller=None):
        
        
        self.log(f"""
        RING RING!
            json_phone2op={json_phone2op},
            json_caller2op={json_caller2op},
            json_caller2caller={json_caller2caller},
            from_caller={from_caller},
            to_caller={to_caller}
        """)

        ## defaults
        unencr_header=b''
        encrypted_message_from_telephone_to_op = b''
        encrypted_message_from_caller_to_op = b''
        encrypted_message_from_caller_to_caller = b''

        ### LAYERS OF ENCRYPTION:
        # 1) unencr header
        # Telephone sends half its and the operator's public keys
        unencr_header = self.pubkey_encr_ + BSEP2 + self.op.pubkey_decr_
        self.log('Layer 1: Unencrypted header:',unencr_header)

        ## Encrypt level 1: from Phone to Op
        if json_phone2op:
            encrypted_message_from_telephone_to_op = self.encrypt_to_send(
                msg_json = json_phone2op,
                from_privkey = self.privkey_,
                to_pubkey = self.op.pubkey_
            )
            self.log('Layer 2: Phone 2 op:',encrypted_message_from_telephone_to_op)

        ## Level 2: from Caller to Op
        if json_caller2op and from_caller:
            encrypted_message_from_caller_to_op = self.encrypt_to_send(
                msg_json = json_caller2op,
                from_privkey = from_caller.privkey_,
                to_pubkey = self.op.pubkey_
            )
            self.log('Layer 3: Caller 2 op:',encrypted_message_from_telephone_to_op)
        
        # 2) Level 3: from Caller to Caller
        if json_caller2caller and from_caller and to_caller:
            encrypted_message_from_caller_to_caller = self.encrypt_to_send(
                msg_json = json_caller,
                from_privkey = from_caller.privkey_,
                to_pubkey = to_caller.pubkey_
            )
            self.log('Layer 3: Caller 2 Caller:',encrypted_message_from_telephone_to_op)
        
        MSG_PIECES = [
            unencr_header,
            encrypted_message_from_telephone_to_op,
            encrypted_message_from_caller_to_op,
            encrypted_message_from_caller_to_caller
        ]
        MSG = BSEP.join(MSG_PIECES)
        MSG_b64 = b64encode(MSG)

        answer = self.send_and_receive(MSG_b64)

        self.log('result from operator?',answer)
        return answer





    
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