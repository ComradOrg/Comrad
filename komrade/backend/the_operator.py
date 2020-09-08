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
        
        from komrade.backend.phonelines import connect_phonelines
        if not TELEPHONE_KEYCHAIN or not OPERATOR_KEYCHAIN:
            OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN = connect_phonelines()
        if not passphrase: self.passphrase=passphrase=getpass.getpass('Hello, this is the Operator speaking. What is the passphrase?\n> ')
        super().__init__(
            name,
            passphrase,
            path_crypt_keys=PATH_CRYPT_OP_KEYS,
            path_crypt_data=PATH_CRYPT_OP_DATA)
        self._keychain = OPERATOR_KEYCHAIN
        
    def ring(self,
        from_caller=None,
        to_caller=None,
        json_phone2phone={}, 
        json_caller2phone={},   # (person) -> operator or operator -> (person)
        json_caller2caller={}):
        
        encr_msg_to_send = super().ring(
            from_phone=self,
            to_phone=self.phone,
            from_caller=from_caller,
            to_caller=to_caller,
            json_phone2phone=json_phone2phone, 
            json_caller2phone=json_caller2phone,   # (person) -> operator
            json_caller2caller=json_caller2caller)

        return self.send(encr_msg_to_send)

    # ends the ring_ring() chain
    def answer_phone(self,data_b64_str):
        # route incoming call from the switchboard
        self.log('Hello, this is the Operator. You said: ',data_b64_str)

        # decode
        data_b64 = data_b64_str.encode()
        data = b64decode(data_b64)
        msg_encr_caller2caller_caller2phone_phone2phone = data
        self.log('msg_encr_caller2caller_caller2phone_phone2phone incoming',msg_encr_caller2caller_caller2phone_phone2phone)

        TOTAL_MSG = {}

        # top layer: phone -> me, the op
        msg_encr_caller2caller_caller2phone = self.unpackage_msg_from(
            msg_encr_caller2caller_caller2phone_phone2phone,
            self.phone
        )
        self.log('Operator unrolled the first layer of encryption:',msg_encr_caller2caller_caller2phone)
        assert type(msg_encr_caller2caller_caller2phone)==dict
        
        # is there another layer?
        msg_d=msg_encr_caller2caller_caller2phone
        _msg=msg_d.get('_msg')
        route=None
        if _msg and type(_msg)==bytes:
            alleged_name = msg_d.get('_from_name')
            alleged_pubkey = msg_d.get('_from_pub')
            if alleged_pubkey and alleged_name:
                alleged_caller = Caller(alleged_name)
                assert alleged_caller.pubkey == alleged_pubkey

                msg_d2 = self.unpackage_msg_from(
                    _msg,
                    caller
                )
                assert type(msg_d2)==dict
                _msg2 = msg_d2.get('_msg')
                route = msg_d2.get('_msg',{}).get('_please')
                # dict_merge(msg_d,msg_d2)
                msg_d['_msg'] = msg_d2
        
        if not route:
            route = msg_d.get('_msg',{}).get('_please',None)
        
        return self.route(msg_d,route)




    def send(self,encr_data_b):
        self.log(type(encr_data_b),encr_data_b,'sending!')
        return encr_data_b


    def route(self, msg_d, route):
        self.log(f'route() got incoming msg_d = {msg_d} and route = {route}')
        if route == 'forge_new_keys':
            return self.forge_new_keys(**msg_d)
        return OPERATOR_INTERCEPT_MESSAGE

    def forge_new_keys(self,**data):
        self.log('about to make some new keys!',data)
        
        # get keys
        forged_keys_plus_id = super().forge_new_keys(**data)

        # return to Telephone/Caller
        return self.ring(json_phone2phone=forged_keys_plus_id)

        
        




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