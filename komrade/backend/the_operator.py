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
        self.log('recv 1: got',data)

        # answer the phone!
        data_in = self.answer_phone(data)
        self.log('recv 2: answer_phone gave me',data_in)

        # route
        encr_result = self.route(data_in)
        self.log('recv 3: route gave me',result)

        # send
        return self.send(encr_result)


    def send(self,encr_data_b):
        # telephone v:
        # unencr_header = self.pubkey_encr_ + BSEP2 + self.op.pubkey_decr_
        unencr_header = self.phone.pubkey_decr_ + BSEP2 + self.op.pubkey_encr_
        self.log('unencr_header',unencr_header)
        
        total_pkg = unencr_header + BSEP + encr_data_b
        self.log('total_pkg',total_pkg)
        total_pkg_b64 = b64encode(total_pkg)
        self.log('total_pkg_b64',total_pkg_b64)

        return total_pkg_b64


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