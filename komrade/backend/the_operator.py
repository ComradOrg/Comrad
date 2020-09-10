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
        
        # decrypt?
        msg_obj.decrypt()

        # carry out message instructions
        resp_msg_obj = self.pronto_pronto(msg_obj) #,route=msg_obj.route)
        self.log('route_result <-',resp_msg_obj)

        # send back down encrypted
        msg_sealed = self.seal_msg(resp_msg_obj.msg_d)

        # return back to phone and back down to chain
        return msg_sealed


    def find_pubkey(self):
        return self.operator_keychain['pubkey']


    def send(self,encr_data_b):
        self.log(type(encr_data_b),encr_data_b,'sending!')
        return encr_data_b

    ### ROUTES
        
    def does_username_exist(self,name,**data):
        pubkey=self.crypt_keys.get(name,prefix='/pubkey/')
        self.log(f'looking for {name}, found {pubkey} as pubkey')
        return bool(pubkey)

    def register_new_user(self,name,pubkey,**data):
        # self.log('setting pubkey under name')
        success,ck,cv = self.crypt_keys.set(name,pubkey,prefix='/pubkey/')
        # self.log('got result from crypt:',res)
        
        # check input back from crypt
        assert cv==pubkey
        assert name==self.crypt_keys.key2hash(name) #(self.crypt_keys.prepare_key()
        
        res = {
            'success':success,
            'pubkey':cv,
            'name':name,
        }
        
        ## success msg
        if success:
            res['status'] = f'''
{OPERATOR_INTRO} I have managed to register user {name}.
I've stored their public key ({b64encode(cv).decode()}) under their name.
I never mention this name directly, but record it only
in a disguised, "hashed" form: by running it through a 1-way 
information process which will always yield the same scrambled result,
but which is unpredictable to anyone without the secret key,
which I keep protected and encrypted on my local hard drive.
The content of tour subsequent data will therefore not only be encrypted,
but its location in my database is obscured, and even I couldn't find it
again unless you gave me exactly what information to run through the 1-way
information scrambler once again.'''
        else:
            res['status']= f'''
{OPERATOR_INTRO}. I'm sorry, but I can'tregister username {name}.
Someone has already registered under that name.
'''
        self.log('Operator returning result:',res)
        return res
        




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