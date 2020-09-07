"""
There is only one operator!
Running on node prime.
"""
# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *


# PATH_OPERATOR_WEB_KEYS_URI = hashish(b'keys')
PATH_OPERATOR_WEB_KEYS_FILE = f'/home/ryan/www/website-komrade/.builtin.keys'
PATH_OPERATOR_WEB_KEYS_URL = f'http://{KOMRADE_ONION}/.builtin.keys'

# print(PATH_OPERATOR_WEB_KEYS_URL)


class TheOperator(Operator):
    """
    The remote operator
    """
    @property
    def phone(self):
        global TELEPHONE
        from komrade.backend.the_telephone import TheTelephone
        if not TELEPHONE: TELEPHONE=TheTelephone(allow_builtin=False)
        return TELEPHONE
    

    def __init__(self, name = OPERATOR_NAME, passphrase='acc', allow_builtin=True):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """
        # init req paths
        # if not os.path.exists(PATH_OPERATOR): os.makedirs(PATH_OPERATOR)
        if not passphrase:
            passphrase=getpass.getpass('Hello, this is the Operator speaking. What is the passphrase?\n> ')
        self.allow_builtin=allow_builtin
        super().__init__(name,passphrase,path_crypt_keys=PATH_CRYPT_OP_KEYS,path_crypt_data=PATH_CRYPT_OP_DATA)

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


def init_operators():

    ## CREATE OPERATOR
    op = Operator(name=OPERATOR_NAME)
    
    # save what we normally save for a client on the server -- The Op is a client from our pov
    
    # take 1
    # op_keys_to_keep_on_client = ['pubkey_decr']
    # op_keys_to_keep_on_3rdparty = ['pubkey_encr','privkey_encr']
    # op_keys_to_keep_on_server = ['adminkey_encr',
    #                             'privkey_decr_encr',
    #                             'privkey_decr_decr',
    #                             'adminkey_decr_encr',
    #                             'adminkey_decr_decr']

    # phone_keys_to_keep_on_client = ['privkey_decr']
    # phone_keys_to_keep_on_3rdparty = ['privkey_encr','pubkey_encr']
    # phone_keys_to_keep_on_server = ['pubkey_decr']

    op_keys_to_keep_on_client = ['pubkey_encr']
    op_keys_to_keep_on_3rdparty = ['pubkey_decr','privkey_decr']
    op_keys_to_keep_on_server = ['adminkey_encr',
                                'privkey_decr_encr',
                                'privkey_decr_decr',
                                'adminkey_decr_encr',
                                'adminkey_decr_decr']

    phone_keys_to_keep_on_client = ['privkey_encr']
    phone_keys_to_keep_on_3rdparty = ['privkey_decr','pubkey_decr']
    phone_keys_to_keep_on_server = ['pubkey_encr']

    op_decr_keys = op.forge_new_keys(
        keys_to_save=op_keys_to_keep_on_server,  # on server only; flipped around
        keys_to_return=op_keys_to_keep_on_client + op_keys_to_keep_on_3rdparty # on clients only
    )
    from pprint import pprint

    ## CREATE TELEPHONE
    phone = Operator(name=TELEPHONE_NAME)

    

    phone_decr_keys = phone.forge_new_keys(
        name=TELEPHONE_NAME,
        keys_to_save=phone_keys_to_keep_on_server,  # on server only
        keys_to_return=phone_keys_to_keep_on_client + phone_keys_to_keep_on_3rdparty   # on clients only
    )

    print('OP KEYS RETURNED')
    pprint(op_decr_keys)


    print('PHONE KEYS RETURNED')
    pprint(phone_decr_keys)



    THIRD_PARTY_DICT = {OPERATOR_NAME:{}, TELEPHONE_NAME:{}}

    for key in op_keys_to_keep_on_3rdparty:
        if key in op_decr_keys:
            THIRD_PARTY_DICT[OPERATOR_NAME][key]=op_decr_keys[key]
    for key in phone_keys_to_keep_on_3rdparty:
        if key in phone_decr_keys:
            THIRD_PARTY_DICT[TELEPHONE_NAME][key]=phone_decr_keys[key]

    STORE_IN_APP = {OPERATOR_NAME:{}, TELEPHONE_NAME:{}}

    for key in op_keys_to_keep_on_client:
        if key in op_decr_keys:
            STORE_IN_APP[OPERATOR_NAME][key]=op_decr_keys[key]
    for key in phone_keys_to_keep_on_client:
        if key in phone_decr_keys:
            STORE_IN_APP[TELEPHONE_NAME][key]=phone_decr_keys[key]

    STORE_IN_APP_pkg = package_for_transmission(STORE_IN_APP[TELEPHONE_NAME]) + BSEP + package_for_transmission(STORE_IN_APP[OPERATOR_NAME])

    THIRD_PARTY_DICT_pkg = package_for_transmission(THIRD_PARTY_DICT[TELEPHONE_NAME]) + BSEP + package_for_transmission(THIRD_PARTY_DICT[OPERATOR_NAME])

    print('store in app =',STORE_IN_APP)
    print('store in web =',THIRD_PARTY_DICT)
    print()


    print('new: make omega key')
    omega_key = KomradeSymmetricKeyWithoutPassphrase()

    STORE_IN_APP_encr = b64encode(omega_key.encrypt(STORE_IN_APP_pkg))
    THIRD_PARTY_totalpkg = b64encode(omega_key.data + BSEP + omega_key.encrypt(THIRD_PARTY_DICT_pkg))

    with open(PATH_BUILTIN_KEYCHAIN,'wb') as of:
        of.write(STORE_IN_APP_encr)
        print('STORE_IN_APP_encr',STORE_IN_APP_encr)
        
    with open(PATH_OPERATOR_WEB_KEYS_FILE,'wb') as of:
        of.write(THIRD_PARTY_totalpkg)
        print('THIRD_PARTY_DICT_encr',THIRD_PARTY_totalpkg)


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