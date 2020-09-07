# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *
from komrade.backend.keymaker import *
from komrade.backend.mazes import *
from komrade.backend.switchboard import *




class Operator(Keymaker):
    
    def __init__(self, name, passphrase=None, keychain = {}, path_crypt_keys=PATH_CRYPT_CA_KEYS, path_crypt_data=PATH_CRYPT_CA_DATA):
        super().__init__(name=name,passphrase=passphrase, keychain=keychain,
                         path_crypt_keys=path_crypt_keys, path_crypt_data=path_crypt_data)
        self.boot(create=False)

    def boot(self,create=False):
         # Do I have my keys?
        have_keys = self.exists()
        
        # If not, forge them -- only once!
        if not have_keys and create:
            self.get_new_keys()

        # load keychain into memory
        self._keychain = self.keychain(force = True)

    
    @property
    def phone(self):
        if hasattr(self,'_phone'): return self._phone
        global TELEPHONE,TELEPHONE_KEYCHAIN
        if TELEPHONE: return TELEPHONE
        from komrade.backend.the_telephone import TheTelephone
        self._phone=TELEPHONE=TheTelephone()
        return TELEPHONE

    @property
    def op(self):
        if hasattr(self,'_phone'): return self._phone
        global OPERATOR,OPERATOR_KEYCHAIN
        if OPERATOR: return OPERATOR
        from komrade.backend.the_operator import TheOperator
        OPERATOR=TheOperator()
        return OPERATOR

    def encrypt_to_send(self,msg_json,from_privkey,to_pubkey):
        if not msg_json or not from_privkey or not to_pubkey:
            self.log('not enough info!')
            return b''
        msg_b = package_for_transmission(msg_json)
        try:
            msg_encr = SMessage(
                from_privkey,
                to_pubkey,
            ).wrap(msg_b)
            return msg_encr
        except ThemisError as e:
            self.log('unable to encrypt to send!',e)
        return b''


    def decrypt_from_send(self,msg_encr,from_pubkey,to_privkey):
        if not msg_encr or not from_pubkey or not to_privkey:
            self.log('not enough info!')
            return b''
        try:
            # decrypt
            msg_b = SMessage(
                to_privkey,
                from_pubkey,
            ).unwrap(msg_encr)
            # decode
            self.log('msg_b??',msg_b)
            msg_json = unpackage_from_transmission(msg_b)
            self.log('msg_json??',msg_json)
            # return
            return msg_json
        except ThemisError as e:
            self.log('unable to decrypt from send!',e)
        return b''


    def encrypt_outgoing(self,
                        json_phone={},
                        json_caller={},
                        from_phone_privkey=None,
                        from_caller_privkey=None,
                        to_pubkey=None,
                        unencr_header=b''):
        
        
        # 2) encrypt to phone
        json_phone_encr = self.encrypt_to_send(json_phone,from_phone_privkey,to_pubkey)
        self.log('json_phone_encr',json_phone_encr)

        # 3) to caller
        json_caller_encr = self.encrypt_to_send(json_caller,from_caller_privkey,to_pubkey)
        self.log()

        # return
        req_data_encr = unencr_header + BSEP + json_phone_encr + BSEP + json_caller_encr
        return req_data_encr

    def reassemble_nec_keys_using_header(self,unencr_header):
        assert unencr_header.count(BSEP2)==1
        phone_pubkey_encr,op_pubkey_decr = unencr_header.split(BSEP2)
        
        # get phone pubkey
        new_phone_keychain = self.phone.keychain(extra_keys={'pubkey_encr':phone_pubkey_encr},force=True)
        new_op_keychain = self.keychain(extra_keys={'pubkey_decr':op_pubkey_decr},force=True)

        phone_pubkey = new_phone_keychain.get('pubkey')
        op_pubkey = new_op_keychain.get('pubkey')

        self.log('reassembled phone/op pubkeys:',phone_pubkey,op_pubkey)
        return (phone_pubkey,op_pubkey)

    def reassemble_necessary_keys_using_decr_phone_data(self,decr_phone_data):
        name=decr_phone_data.get('name')
        if not name: return None

        try:
            caller = Caller(name)
            self.log('got caller on phone',name,caller)
            return caller.pubkey_
        except:
            return

        
    def decrypt_incoming(self,data_b64_s):
        assert type(data_b64_s) == str

        if not isBase64(data_b64_s):
            self.log('incoming data not b64')
            return OPERATOR_INTERCEPT_MESSAGE

        data_b64_b = data_b64_s.encode()
        data = b64decode(data_b64_b)

        # step 1 split:
        print('!?!?!?',type(data),data)
        unencr_header,data_encr_by_phone,data_encr_by_caller = data.split(BSEP)
        data_unencr_by_phone,data_unencr_by_caller = None,None

        # set up
        DATA = {}

        # assuming the entire message is to me, whoever I am
        to_privkey = self.privkey()
        self.log('keychain',self.keychain())
        self.log('to_privkey',to_privkey)
        exit()

        # get other keys from halfkeys
        phone_pubkey,op_pubkey = self.reassemble_nec_keys_using_header(unencr_header)

        # 2) decrypt from phone
        self.log('data_encr_by_phone',data_encr_by_phone)
        self.log('phone_pubkey',phone_pubkey)
        self.log('to_privkey',to_privkey)
        data_by_phone = self.decrypt_from_send(data_encr_by_phone,phone_pubkey,to_privkey)
        self.log('data_by_phone',data_by_phone)

        # 3) decrypt from caller
        # caller_pubkey = self.reassemble_necessary_keys_using_decr_phone_data(data_by_phone)
        # data_by_caller = self.decrypt_from_send(data_encr_by_caller,caller_pubkey,to_privkey)

        # return
        # req_data_encr = unencr_header + BSEP + data_by_phone + BSEP + data_by_caller
        
        self.log('data_by_phone',data_by_phone)
        # self.log('data_by_caller',data_by_caller)
        stop
        
        return req_data_encr






### CREATE PRIME ENTITIES
def create_phonelines():
    ## CREATE OPERATOR
    op = Operator(name=OPERATOR_NAME)
    op_keys_to_keep_on_client = ['pubkey_decr']  # sent TO operator
    op_keys_to_keep_on_3rdparty = ['pubkey_encr']  # dl by op
    op_keys_to_keep_on_server = [
        'privkey_encr','privkey_decr_encr','privkey_decr_decr',
        'adminkey_encr','adminkey_decr_encr','adminkey_decr_decr']

    ## create phone
    phone = Operator(name=TELEPHONE_NAME)
    phone_keys_to_keep_on_client = ['privkey_decr']
    phone_keys_to_keep_on_3rdparty = ['pubkey_encr','privkey_encr']  # dl by phone
    phone_keys_to_keep_on_server = ['pubkey_decr']  # sent to phone

    # create keys for Op
    op_decr_keys = op.forge_new_keys(
        keys_to_save=op_keys_to_keep_on_server,  # on server only; flipped around
        keys_to_return=op_keys_to_keep_on_client + op_keys_to_keep_on_3rdparty # on clients only
    )

    # create keys for phone
    phone_decr_keys = phone.forge_new_keys(
        name=TELEPHONE_NAME,
        keys_to_save=phone_keys_to_keep_on_server,  # on server only
        keys_to_return=phone_keys_to_keep_on_client + phone_keys_to_keep_on_3rdparty   # on clients only
    )

    ## store remote keys
    THIRD_PARTY_DICT = {OPERATOR_NAME:{}, TELEPHONE_NAME:{}}
    for key in op_keys_to_keep_on_3rdparty:
        if key in op_decr_keys:
            THIRD_PARTY_DICT[OPERATOR_NAME][key]=op_decr_keys[key]
    for key in phone_keys_to_keep_on_3rdparty:
        if key in phone_decr_keys:
            THIRD_PARTY_DICT[TELEPHONE_NAME][key]=phone_decr_keys[key]

    # store local keys
    STORE_IN_APP = {OPERATOR_NAME:{}, TELEPHONE_NAME:{}}
    for key in op_keys_to_keep_on_client:
        if key in op_decr_keys:
            STORE_IN_APP[OPERATOR_NAME][key]=op_decr_keys[key]
    for key in phone_keys_to_keep_on_client:
        if key in phone_decr_keys:
            STORE_IN_APP[TELEPHONE_NAME][key]=phone_decr_keys[key]

    # package
    STORE_IN_APP_pkg = package_for_transmission(STORE_IN_APP[TELEPHONE_NAME]) + BSEP + package_for_transmission(STORE_IN_APP[OPERATOR_NAME])
    THIRD_PARTY_DICT_pkg = package_for_transmission(THIRD_PARTY_DICT[TELEPHONE_NAME]) + BSEP + package_for_transmission(THIRD_PARTY_DICT[OPERATOR_NAME])

    # encrypt
    omega_key = KomradeSymmetricKeyWithoutPassphrase()
    STORE_IN_APP_encr = b64encode(omega_key.encrypt(STORE_IN_APP_pkg))
    THIRD_PARTY_totalpkg = b64encode(omega_key.data + BSEP + omega_key.encrypt(THIRD_PARTY_DICT_pkg))

    # save
    with open(PATH_BUILTIN_KEYCHAIN,'wb') as of:
        of.write(STORE_IN_APP_encr)
        print('STORE_IN_APP_encr',STORE_IN_APP_encr)
        
    with open(PATH_OPERATOR_WEB_KEYS_FILE,'wb') as of:
        of.write(THIRD_PARTY_totalpkg)
        print('THIRD_PARTY_DICT_encr',THIRD_PARTY_totalpkg)


def connect_phonelines():
    # globals
    global OMEGA_KEY,OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN
    if OMEGA_KEY and OPERATOR_KEYCHAIN and TELEPHONE_KEYCHAIN:
        return (OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN)

    print('\n\n\n\nCONNECTING PHONELINES!\n\n\n\n')

    # import
    from komrade.backend.mazes import tor_request
    from komrade.backend import PATH_OPERATOR_WEB_KEYS_URL

    # load local keys
    if not os.path.exists(PATH_BUILTIN_KEYCHAIN):
        print('builtin keys not present??')
        return
    with open(PATH_BUILTIN_KEYCHAIN,'rb') as f:
        local_builtin_keychain_encr = b64decode(f.read())

    # load remote keys
    print('??',PATH_OPERATOR_WEB_KEYS_URL)
    r = komrade_request(PATH_OPERATOR_WEB_KEYS_URL)
    if r.status_code!=200:
        print('cannot authenticate the keymakers')
        return
    
    # unpack remote pkg
    pkg = b64decode(r.text)
    OMEGA_KEY_b,remote_builtin_keychain_encr = pkg.split(BSEP)
    OMEGA_KEY = KomradeSymmetricKeyWithoutPassphrase(key=OMEGA_KEY_b)
    remote_builtin_keychain = OMEGA_KEY.decrypt(remote_builtin_keychain_encr)
    remote_builtin_keychain_phone,remote_builtin_keychain_op = remote_builtin_keychain.split(BSEP)
    remote_builtin_keychain_phone_json = unpackage_from_transmission(remote_builtin_keychain_phone)
    remote_builtin_keychain_op_json = unpackage_from_transmission(remote_builtin_keychain_op)    
    print('remote_builtin_keychain_phone_json',remote_builtin_keychain_phone_json)
    print('remote_builtin_keychain_op_json',remote_builtin_keychain_op_json)
    
    # unpack local pkg
    local_builtin_keychain = OMEGA_KEY.decrypt(local_builtin_keychain_encr)
    local_builtin_keychain_phone,local_builtin_keychain_op = local_builtin_keychain.split(BSEP)
    local_builtin_keychain_phone_json = unpackage_from_transmission(local_builtin_keychain_phone)
    local_builtin_keychain_op_json = unpackage_from_transmission(local_builtin_keychain_op)
    print('local_builtin_keychain_phone_json',local_builtin_keychain_phone_json)
    print('local_builtin_keychain_op_json',local_builtin_keychain_op_json)

    # set builtin keychains
    TELEPHONE_KEYCHAIN={}
    OPERATOR_KEYCHAIN={}
    dict_merge(TELEPHONE_KEYCHAIN,local_builtin_keychain_phone_json)
    dict_merge(OPERATOR_KEYCHAIN,local_builtin_keychain_op_json)
    dict_merge(TELEPHONE_KEYCHAIN,remote_builtin_keychain_phone_json)
    dict_merge(OPERATOR_KEYCHAIN,remote_builtin_keychain_op_json)
    
    return (OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN)

    # # load prime objects?
    # from komrade.backend.the_operator import TheOperator
    # from komrade.backend.the_telephone import TheTelephone
    # OPERATOR = TheOperator(keychain=OPERATOR_KEYCHAIN)
    # TELEPHONE = TheTelephone(keychain=TELEPHONE_KEYCHAIN)
    
    # return (OPERATOR,TELEPHONE)