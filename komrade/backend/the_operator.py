"""
There is only one operator!
Running on node prime.
"""
# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *


# print(PATH_OPERATOR_WEB_KEYS_URL)


class TheOperator(Operator):
    """
    The remote operator
    """
    @property
    def phone(self):
        global TELEPHONE
        from komrade.backend.the_telephone import TheTelephone
        if not TELEPHONE: TELEPHONE=TheTelephone()
        return TELEPHONE
    

    def __init__(self, name = OPERATOR_NAME, passphrase='acc'):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """
        # init req paths
        # if not os.path.exists(PATH_OPERATOR): os.makedirs(PATH_OPERATOR)
        global OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN
        if not TELEPHONE_KEYCHAIN or not OPERATOR_KEYCHAIN:
            OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN = connect_phonelines()
        if not passphrase: self.passphrase=passphrase=getpass.getpass('Hello, this is the Operator speaking. What is the passphrase?\n> ')
        super().__init__(
            name,
            passphrase,
            path_crypt_keys=PATH_CRYPT_OP_KEYS,
            path_crypt_data=PATH_CRYPT_OP_DATA)
        self._keychain = OPERATOR_KEYCHAIN
        


    def recv(self,data):
        # decrypt
        data_in = self.decrypt_incoming(data)

        # route
        result = self.route(data_json)
        
        # encrypt
        data_out = self.encrypt_outgoing(result)

        # send
        return self.send(res)


    def send(self,res):
        if not len(res)==2:
            self.log('!! error. argument to send() must be: (json_tophone,json_tosender)')
            return
        
        msg_tophone,msg_tocaller = res
        caller=None
        if msg_tocaller and 'name' in msg_tophone:
            caller = Operator(msg_tophone['name'])
        self.log('send!',msg_tophone,msg_tocaller,caller)
        data = self.encrypt_information(json_phone=msg_tophone,json_caller=caller)
        self.log('got back encr:',data)
        return data


    def route(self, data):
        res=None
        route = data.get('_route')
        if not route: return OPERATOR_INTERCEPT_MESSAGE
        del data['_route']

        if route == 'forge_new_keys':
            res = self.forge_new_keys(**data)
        else:
            res = OPERATOR_INTERCEPT_MESSAGE
        return res# 'success!'

    def forge_new_keys(self,**data):
        # get keys
        res = super().forge_new_keys(**data)
        pkg={}
        pkg['name']=data.get('name')
        pkg['_keychain']=res
        self.log('returned keys from keymaker.forge_new_keys:','\n'.join(res.keys()))
        
        # return to_phone,to_caller
        return (pkg,{})




def test_op():
    from komrade.backend.the_telephone import TheTelephone

    
    op = TheOperator()
    # op.boot()
    
    keychain_op = op.keychain(force=True)

    
    phone = TheTelephone()
    # phone.boot()
    keychain_ph = phone.keychain(force=True)
    
    
    from pprint import pprint
    print('REASSEMBLED OPERATOR KEYCHAIN')
    pprint(keychain_op)
    # stop

    print('REASSEMBLED TELEPHONE KEYCHAIN')
    pprint(keychain_ph)
    
    # print(op.pubkey(keychain=keychain))
    # print(op.crypt_keys.get(op.pubkey(), prefix='/privkey_encr/'))
    # print(op.crypt_keys.get(op.name, prefix='/pubkey_encr/'))
    # print(op.pubkey_)


    # stop
    
    # pubkey = op.keychain()['pubkey']
    # pubkey_b64 = b64encode(pubkey)
    # print(pubkey)

if __name__ == '__main__': test_op()