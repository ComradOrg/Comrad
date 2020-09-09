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
        super().__init__(
            name,
            passphrase,
            path_crypt_keys=PATH_CRYPT_OP_KEYS,
            path_crypt_data=PATH_CRYPT_OP_DATA
        )
        self._keychain = self.operator_keychain
        
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
    def answer_phone(self,data_b):
        # route incoming call from the switchboard
        self.log('Hello, this is the Operator. You said: ',data_b)

        # unseal
        msg_obj = self.unseal_msg(
            data_b,
            from_whom=self.phone
        )
        self.log(f'Operator understood message: {msg_obj} {msg_obj.route}')
        
        # carry out message instructions
        resp_msg_obj = self.route_msg(msg_obj) #,route=msg_obj.route)
        self.log('route_result <-',resp_msg_obj)

        # should be encrypted already
        assert resp_msg_obj.is_encrypted
        # it should be pointing back from me to the telephone
        assert resp_msg_obj.callee.pubkey==self.phone.pubkey
        assert resp_msg_obj.caller.pubkey==self.pubkey
        
        # send back down encrypted
        msg_sealed = self.seal_msg(resp_msg_obj.msg_d)

        # return back to phone and back down to chain
        return msg_sealed


    def find_pubkey(self):
        return self.operator_keychain['pubkey']


    def send(self,encr_data_b):
        self.log(type(encr_data_b),encr_data_b,'sending!')
        return encr_data_b


    # def route(self, msg_obj):
    #     if not msg_obj.route:
    #         # nothign explicitly requested yet?
    #         # can we pass the msg on?
    #         if msg_obj.has_embedded_msg:

    #         self.route(msg_obj, route=msg_obj)
        
    #     # self.log('my messages:',msg_obj.messages)

        

    #     if not route: raise KomradeException('no route!')
        
    #     # what we working with?
    #     self.log(f'route() got incoming msg data = {data} and route = {route}')
        
    #     ## hard code the acceptable routes
    #     if route == 'forge_new_keys':
    #         return self.forge_new_keys(data)
    #     elif route == 'does_username_exist':
    #         return self.does_username_exist(data)
        
    #     # otherwise, hang up and try again
    #     return OPERATOR_INTERCEPT_MESSAGE





    ### ROUTES
    def forge_new_keys(self,msg_obj):
        self.log('about to make some new keys!',msg_obj.msg_d)
        # return {'_route':'well_hello_to_you_too'}
        
        # get keys
        forged_keys_plus_id = super().forge_new_keys(**data)

        # return to Telephone/Caller
        return forged_keys_plus_id
        
    def does_username_exist(self,data):
        # find pubkey?
        name=data.get('name')

        pubkey=self.crypt_keys.get(name,prefix='/pubkey/')
        self.log(f'looking for {name}, found {pubkey} as pubkey')
        return bool(pubkey)

        




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