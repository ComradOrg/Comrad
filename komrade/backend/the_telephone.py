# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *
from komrade.backend.operators import *
from komrade.backend.mazes import *

### ACTUAL PHONE CONNECTIONS
class TheTelephone(Logger):
    """
    API client class for Caller to interact with The Operator.
    """
    def __init__(self, caller):
        self.caller = caller

    @property
    def op_pubkey(self):
        return b64decode(OPERATOR_PUBKEY)

    # def dial_operator(self,msg):
    #     msg=msg.replace('/','_')
    #     URL = OPERATOR_API_URL + msg + '/'
    #     self.log("DIALING THE OPERATOR:",URL)
    #     r=tor_request(URL)
    #     print(r)
    #     print(r.text)
    #     return r
    async def dial_operator(self,msg):
        msg=msg.replace('/','_')
        URL = OPERATOR_API_URL + msg + '/'
        self.log("DIALING THE OPERATOR:",URL)
        try:
            r=await tor_request_async(URL)
        except TypeError:
            return r
        return r

    async def req(self,json_coming_from_phone={},json_coming_from_caller={}):
        # Two parts of every request:
        
        # 1) only overall encryption layer E2EE Telephone -> Operator:

        req_data = []        
        if json_coming_from_phone:
            json_coming_from_phone_s = json.dumps(json_coming_from_phone)
            json_coming_from_phone_b = json_coming_from_phone_s.encode()
            #json_coming_from_phone_b_encr = SMessage(TELEPHONE_PRIVKEY,OPERATOR_PUBKEY).wrap(json_coming_from_phone_b)
        else:
            json_coming_from_phone_b=b''

        # 2) (optional) extra E2EE encrypted layer Caller -> Operator
        if json_coming_from_caller:
            json_coming_from_caller_s = json.dumps(json_coming_from_caller)
            json_coming_from_caller_b = json_coming_from_caller_s.encode()
            op_pubkey
            json_coming_from_caller_b_encr = SMessage(self.caller.privkey_,self.op_pubkey).wrap(json_coming_from_caller_b)
        else:
            json_coming_from_caller_b_encr = b''

        # encrypt whole package E2EE, Telephone to Operator
        req_data = json_coming_from_phone_b + BSEP + json_coming_from_caller_b_encr
        req_data_encr = SMessage(
            b64decode(TELEPHONE_PRIVKEY),
            b64decode(OPERATOR_PUBKEY)
        ).wrap(req_data)
        req_data_encr_b64 = b64encode(req_data_encr)
        self.log('req_data_encr_b64 <--',req_data_encr_b64)

        # send!
        req_data_encr_b64_str = req_data_encr_b64.decode('utf-8')
        
        # escape slashes
        req_data_encr_b64_str_esc = req_data_encr_b64_str.replace('/','_')

        try:
            res = await self.dial_operator(req_data_encr_b64_str)
        except TypeError:
            res = None
        self.log('result from operator?',res)
        return res


    async def forge_new_keys(self, name, pubkey_is_public=False):
        req_json = {'_route':'forge_new_keys','name':name, 'pubkey_is_public':pubkey_is_public}
        # req_json_s = jsonify(req_json)
        try:
            return await self.req(json_coming_from_phone = req_json)
        except TypeError:
            return None


    
def test_call():
    caller = Operator('marx3') #Caller('marx')
    # caller.boot(create=True)
    # print(caller.keychain())
    phone = TheTelephone(caller=caller)
    # req_json = {'_route':'forge_new_keys','name':name, 'pubkey_is_public':pubkey_is_public}}
    # req_json_s = jsonify(req_json)
    # res = phone.req({'forge_new_keys':{'name':'marx', 'pubkey_is_public':True}})
    # print(res)
    asyncio.run(phone.forge_new_keys('marx4'))

    print('YEAH COOL')

## main
if __name__=='__main__': test_call()