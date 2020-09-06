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
        super().__init__(
            name=TELEPHONE_NAME,
            path_crypt_keys=PATH_CRYPT_CA_KEYS,
            path_crypt_data=PATH_CRYPT_CA_KEYS
        )

    @property
    def op(self):
        global OPERATOR
        from komrade.backend.the_operator import TheOperator
        if not OPERATOR: OPERATOR=TheOperator()
        return OPERATOR

    async def dial_operator(self,msg):
        msg=msg.replace('/','_')
        URL = OPERATOR_API_URL + msg + '/'
        self.log("DIALING THE OPERATOR:",URL)
        try:
            r=await tor_request_async(URL)
        except TypeError:
            return r
        return r

    async def req(self,json_coming_from_phone={},json_coming_from_caller={},caller=None,json_unencrypted={}):
        if not caller: caller=self.caller
        # Three parts of every request:

        # 0) Unencrypted. do not use except for very specific minimal reasons!
        # the one being: giving the operator half his private key back:
        # which we have but he doesn't 
        if not '_keychain' in json_unencrypted: 
            json_unencrypted['_keychain']={}
        _kc = json_unencrypted['_keychain']
        if not 'privkey_decr' in _kc: 
            _kc['privkey_decr'] = b64encode(self.op.privkey_decr_).decode()
        self.log('REQ!!!!!',_kc)
        
        if json_unencrypted:
            json_unencrypted_s = json.dumps(json_unencrypted)
            json_unencrypted_b = json_unencrypted_s.encode()
        else:
            json_unencrypted_b = b''
        
        self.log('json_unencrypted_b',json_unencrypted_b)

        # 1) only overall encryption layer E2EE Telephone -> Operator:
        if json_coming_from_phone:
            json_coming_from_phone_s = json.dumps(json_coming_from_phone)
            json_coming_from_phone_b = json_coming_from_phone_s.encode()
            json_coming_from_phone_b_encr = SMessage(self.privkey_,self.op.pubkey_).wrap(json_coming_from_phone_b)
        else:
            json_coming_from_phone_b=b''

        # 2) (optional) extra E2EE encrypted layer Caller -> Operator
        if json_coming_from_caller and caller:
            json_coming_from_caller_s = json.dumps(json_coming_from_caller)
            json_coming_from_caller_b = json_coming_from_caller_s.encode()
            json_coming_from_caller_b_encr = SMessage(caller.privkey_,self.op.pubkey_).wrap(json_coming_from_caller_b)
        else:
            json_coming_from_caller_b_encr = b''

        # encrypt whole package E2EE, Telephone to Operator
        req_data_encr = json_unencrypted_b + BSEP + json_coming_from_phone_b_encr + BSEP + json_coming_from_caller_b_encr
        # req_data_encr = SMessage(self.privkey_,self.op.pubkey_).wrap(req_data)
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