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
        

    def dial_operator(self,msg):
        msg=msg.replace('/','_')
        URL = OPERATOR_API_URL + msg + '/'
        self.log("DIALING THE OPERATOR:",URL)
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
    def ask_operator(self,json_phone={},json_caller={},caller=None):
        if not caller: caller=self.caller
        self.log(f"""
        RING RING!
        caller = {caller}
        json_phone  = {json_phone}
        json_caller = {json_caller}""")

        print('XXXXX',type(self),self._keychain)
        print('YYYYY',self.keychain())
        # stop

        self.log('op_keychain',self.op.keychain())


        # 1) unencr header
        # telephone_pubkey_decr | op_pubkey_decr | op_privkey_decr
        unencr_header = self.pubkey_decr_ + BSEP2 + self.op.pubkey_encr_

        # 2) caller privkey?
        from_caller_privkey=caller.privkey_ if caller and json_caller else None

        # encrypt data
        encrypted_message_to_operator = self.encrypt_outgoing(
            json_phone=json_phone,
            json_caller=json_caller,
            from_phone_privkey=phone_keychain['privkey'],
            from_caller_privkey=from_caller_privkey,
            to_pubkey=op_keychain['pubkey'],
            unencr_header=unencr_header
        )

        # send
        answer = self.dial_operator(encrypted_message_to_operator)

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