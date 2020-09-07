# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *

### ACTUAL PHONE CONNECTIONS
class TheTelephone(Operator):
    """
    API client class for Caller to interact with The Operator.
    """
    def __init__(self, caller=None, allow_builtin=True):
        super().__init__(
            name=TELEPHONE_NAME,
            path_crypt_keys=PATH_CRYPT_CA_KEYS,
            path_crypt_data=PATH_CRYPT_CA_KEYS
        )
        self.caller=caller
        self.allow_builtin=allow_builtin

    # @property
    # def op(self):
    #     global OPERATOR
    #     from komrade.backend.the_operator import TheOperator
    #     if not OPERATOR: OPERATOR=TheOperator()
    #     return OPERATOR

    async def dial_operator(self,msg):
        msg=msg.replace('/','_')
        URL = OPERATOR_API_URL + msg + '/'
        self.log("DIALING THE OPERATOR:",URL)
        try:
            r=await tor_request_async(URL)
        except TypeError:
            return r
        return r




    async def req(self,json_coming_from_phone={},json_coming_from_caller={},caller=None):
        if not caller: caller=self.caller
        self.log(f"""
        RING RING!
        caller = {caller}
        json_coming_from_phone  = {json_coming_from_phone}
        json_coming_from_caller = {json_coming_from_caller}""")
        

        # keychain = self.keychain(allow_builtin=self.allow_builtin, force=True)
        # self.log('about to make a call. my keychain?',keychain)
        # stop
        # stop
        # Three parts of every request:

        # 0) Unencrypted. do not use except for very specific minimal reasons!
        # exchange half-complete pieces of info, both of which necessary for other
        

        unencr_header = OPERATOR_KEYCHAIN['privkey_decr'] + BSEP2 + TELEPHONE_NAME['pubkey_decr']
        self.log('unencr_header',unencr_header)

        # ewrwerewrwerw
        # 1) only overall encryption layer E2EE Telephone -> Operator:
        if json_coming_from_phone:
            json_coming_from_phone_s = json.dumps(json_coming_from_phone)
            json_coming_from_phone_b = json_coming_from_phone_s.encode()
            json_coming_from_phone_b_encr = SMessage(
                TELEPHONE_KEYCHAIN['privkey'],
                OPERATOR_KEYCHAIN['pubkey']
            ).wrap(json_coming_from_phone_b)
        else:
            json_coming_from_phone_b=b''

        # 2) (optional) extra E2EE encrypted layer Caller -> Operator
        if json_coming_from_caller and caller:
            json_coming_from_caller_s = json.dumps(json_coming_from_caller)
            json_coming_from_caller_b = json_coming_from_caller_s.encode()
            json_coming_from_caller_b_encr = SMessage(
                caller.privkey_,
                OPERATOR_KEYCHAIN['pubkey']
            ).wrap(json_coming_from_caller_b)
        else:
            json_coming_from_caller_b_encr = b''

        
        

        req_data_encr = unencr_header + BSEP + json_coming_from_phone_b_encr + BSEP + json_coming_from_caller_b_encr
        self.log('req_data_encr',req_data_encr)
        # sewerwe
        # req_data_encr = SMessage(self.privkey_,self.op.pubkey_).wrap(req_data)
        req_data_encr_b64 = b64encode(req_data_encr)
        self.log('req_data_encr_b64 <--',req_data_encr_b64)

        # send!
        req_data_encr_b64_str = req_data_encr_b64.decode('utf-8')

        try:
            res = await self.dial_operator(req_data_encr_b64_str)
        except TypeError:
            res = None
        self.log('result from operator?',res)
        return res





    
def test_call():
    caller = Caller('marx33') #Caller('marx')
    # caller.boot(create=True)
    # print(caller.keychain())
    # phone = TheTelephone()
    # req_json = {'_route':'forge_new_keys','name':name, 'pubkey_is_public':pubkey_is_public}}
    # req_json_s = jsonify(req_json)
    # res = phone.req({'forge_new_keys':{'name':'marx', 'pubkey_is_public':True}})
    # print(res)
    asyncio.run(caller.forge_new_keys())

    print('YEAH COOL')

## main
if __name__=='__main__': test_call()