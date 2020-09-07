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
        

    def decrypt_incoming(self,data):
        # step 1 split:
        data_unencr,data_encr_by_phone,data_encr_by_caller = data.split(BSEP)
        data_unencr_by_phone,data_unencr_by_caller = None,None
        
        self.log('data_unencr =',data_unencr)
        self.log('data_encr_by_phone =',data_encr_by_phone)
        self.log('data_encr_by_caller =',data_encr_by_caller)

        DATA = {}
        # stop1
        PHONE_PUBKEY=None
        MY_PRIVKEY=None
        
        # Scan unencrypted area for half-keys
        if data_unencr:
            self.log('unencrypted data:',data_unencr)
            assert data_unencr.count(BSEP2)==1
            my_privkey_decr,phone_pubkey_decr = data_unencr.split(BSEP2)
            self.log('my_privkey_decr',my_privkey_decr)
            self.log('phone_pubkey_decr',phone_pubkey_decr)

            # get phone pubkey
            new_phone_keychain = self.phone.keychain(extra_keys={'pubkey_decr':phone_pubkey_decr},force=True)
            new_op_keychain = self.keychain(extra_keys={'privkey_decr':my_privkey_decr},force=True)

            PHONE_PUBKEY = new_phone_keychain.get('pubkey')
            MY_PRIVKEY = new_op_keychain.get('privkey')
            
        # Scan phone-encrypted area for json dictionary
        if data_encr_by_phone:
            # then try to unwrap telephone encryption
            if not MY_PRIVKEY or not PHONE_PUBKEY:
                self.log('!! could not assemble my or phone\'s keys. failing.')
                return OPERATOR_INTERCEPT_MESSAGE
            try:
                data_unencr_by_phone = SMessage(MY_PRIVKEY, PHONE_PUBKEY).unwrap(data_encr_by_phone)
                self.log('decrypted data !!!:',data_unencr_by_phone)
            except ThemisError as e:
                self.log('not really from the telephone?',e)
                return OPERATOR_INTERCEPT_MESSAGE
            
            data_unencr_by_phone_json = unpackage_from_transmission(data_unencr_by_phone)
            assert type(data_unencr_by_phone_json) == dict
            dict_merge(DATA, data_unencr_by_phone_json)


        if data_encr_by_caller and 'name' in data_unencr_by_phone:
            name=data_unencr_by_phone['name']

            try:
                caller = Caller(name)
                self.log('got caller on phone',name,caller)
                data_unencr_by_caller = SMessage(MY_PRIVKEY, caller.pubkey_).unwrap(data_encr_by_caller)
                self.log('decrypted data from caller!!!:',data_unencr_by_caller)
            except ThemisError as e:
                self.log('not really from caller?',e)
                return OPERATOR_INTERCEPT_MESSAGE

            data_unencr_by_caller_json = unpackage_from_transmission(data_unencr_by_caller)
            assert type(data_unencr_by_caller_json) == dict
            dict_merge(DATA, data_unencr_by_caller_json)

        return DATA


    def encrypt_outgoing(self,json_phone={},json_caller={},caller=None):
        # 1)
        unencr_header = self.privkey_encr_ + BSEP2 + self.phone.pubkey_encr_
        self.log('unencr_header',unencr_header)

        # 2) encrypt to phone
        if json_phone:
            json_phone_b = package_for_transmission(json_phone)
            try:
                json_phone_b_encr = SMessage(
                    self.privkey_,
                    self.phone.pubkey_
                ).wrap(json_phone_b)
            except ThemisError as e:
                self.log('unable to send to phone!',e)
                return OPERATOR_INTERCEPT_MESSAGE
        else:
            json_phone_b=b''

        # 3) to caller
        if json_caller and caller:
            json_caller_b = package_for_transmission(json_caller)
            try:
                json_caller_b_encr = SMessage(
                    caller.privkey_,
                    self.pubkey_
                ).wrap(json_caller_b)
            except ThemisError as e:
                self.log('unable to send to caller!',e)
                return OPERATOR_INTERCEPT_MESSAGE
        else:
            json_caller_b_encr = b''

        req_data_encr = unencr_header + BSEP + json_phone_b_encr + BSEP + json_caller_b_encr
        return req_data_encr


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