# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *
from komrade.backend.keymaker import *
from komrade.backend.mazes import *
from komrade.backend.switchboard import *




class Operator(Keymaker):
    
    def __init__(self, name, passphrase=DEBUG_DEFAULT_PASSPHRASE, keychain = {}, path_crypt_keys=PATH_CRYPT_CA_KEYS, path_crypt_data=PATH_CRYPT_CA_DATA):
        super().__init__(name=name,passphrase=passphrase, keychain=keychain,
                         path_crypt_keys=path_crypt_keys, path_crypt_data=path_crypt_data)
        self.boot(create=False)

    def boot(self,create=False):
         # Do I have my keys?
        have_keys = self.exists()
        
        # If not, forge them -- only once!
        if not have_keys and create:
            self.get_new_keys()
        
    
    @property
    def phone(self):
        from komrade.backend.the_telephone import TheTelephone
        if type(self)==TheTelephone: return self

        if hasattr(self,'_phone'): return self._phone

        global TELEPHONE,TELEPHONE_KEYCHAIN
        if TELEPHONE: return TELEPHONE

        self._phone=TELEPHONE=TheTelephone()

        return TELEPHONE

    @property
    def op(self):
        from komrade.backend.the_operator import TheOperator
        if type(self)==TheOperator: return self

        if hasattr(self,'_op'): return self._op

        global OPERATOR,OPERATOR_KEYCHAIN
        if OPERATOR: return OPERATOR
        
        self._op=OPERATOR=TheOperator()
        
        return OPERATOR

    def encrypt_to_send(self,msg_json,from_privkey,to_pubkey):
        self.log('msg_json',msg_json)
        self.log('from_privkey',from_privkey)
        self.log('to_pubkey',to_pubkey)
        if not msg_json or not from_privkey or not to_pubkey:
            self.log('not enough info!',msg_json,from_privkey,to_pubkey)
            whattttttt
            return b''
        self.log('packing for transmission: msg_json',type(msg_json),msg_json)
        msg_b = package_for_transmission(msg_json)
        self.log('packing for transmission: msg_b',type(msg_b),msg_b)
        # try:
        msg_encr = SMessage(
            from_privkey,
            to_pubkey,
        ).wrap(msg_b)
        self.log('msg_encr',msg_encr)
        # stop
        return msg_encr
        # except ThemisError as e:
            # self.log('unable to encrypt to send!',e)
        # return b''


    def decrypt_from_send(self,msg_encr,from_pubkey,to_privkey):
        if not msg_encr or not from_pubkey or not to_privkey:
            self.log('not enough info!',msg_encr,from_pubkey,to_privkey)
            return {}
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
        return {}



    def write_to(self,another):
        pass


    # async def req(self,json_phone={},json_caller={},caller=None):
    def ring_ring(self,
            from_phone=None,
            to_phone=None,
            
            from_caller=None,
            to_caller=None,
            
            json_phone2phone={}, 
            json_caller2phone={},   # (person) -> operator or operator -> (person)
            json_caller2caller={}):
            
        
        self.log(f"""
        RING RING!
            from_phone={from_phone}, to_phone={to_phone},
            from_caller={from_caller}, to_caller={to_caller},
            json_phone2phone={json_phone2phone},
            json_caller2phone={json_caller2phone},
            json_caller2caller={json_caller2caller},
        """)

        ## defaults
        unencr_header=b''
        encrypted_message_from_telephone_to_op = b''
        encrypted_message_from_caller_to_op = b''
        encrypted_message_from_caller_to_caller = b''

        print('uri phone',from_phone.uri_id)
        from_phone_keychain = from_phone.keychain()

        

        from_phone_pubkey_encr=from_phone_keychain.get('pubkey_encr')
        from_phone_privkey=from_phone_keychain.get('privkey')
        
        to_phone_keychain = to_phone.keychain()
        to_phone_pubkey_decr=to_phone_keychain.get('pubkey_decr')
        to_phone_pubkey=to_phone_keychain.get('pubkey')

        self.log('from_phone',type(from_phone),'to_phone',type(to_phone))
        self.log('from_phone_keychain',from_phone_keychain)
        self.log('to_phone_keychain',to_phone_keychain)


        ### LAYERS OF ENCRYPTION:
        # 1) unencr header
        # Telephone sends half its and the operator's public keys
        self.log('Layer 1: from_phone_pubkey_encr header:',from_phone_pubkey_encr)
        self.log('Layer 1: to_phone_pubkey_decr header:',to_phone_pubkey_decr)
        
        unencr_header = from_phone_pubkey_encr + BSEP2 + to_phone_pubkey_decr
        self.log('Layer 1: Unencrypted header:',unencr_header)

        ## Encrypt level 1: from Phone to Op
        if json_phone2phone:
            encrypted_message_from_telephone_to_op = self.encrypt_to_send(
                msg_json = json_phone2phone,
                from_privkey = from_phone_privkey,
                to_pubkey = to_phone_pubkey
            )
            self.log('Layer 2: Phone 2 op:',encrypted_message_from_telephone_to_op)

        ## Level 2: from Caller to Op
        if json_caller2phone and from_caller:
            encrypted_message_from_caller_to_op = self.encrypt_to_send(
                msg_json = json_caller2phone,
                from_privkey = from_caller.keychain().get('privkey'),
                to_pubkey = to_phone_pubkey
            )
            self.log('Layer 3: Caller 2 op:',encrypted_message_from_telephone_to_op)
        
        # 2) Level 3: from Caller to Caller
        if json_caller2caller and from_caller and to_caller:
            encrypted_message_from_caller_to_caller = self.encrypt_to_send(
                msg_json = json_caller2caller,
                from_privkey = from_caller.keychain().get('privkey'),
                to_pubkey = to_caller.keychain().get('pubkey')
            )
            self.log('Layer 3: Caller 2 Caller:',encrypted_message_from_telephone_to_op)
        
        MSG_PIECES = [
            unencr_header,
            encrypted_message_from_telephone_to_op,
            encrypted_message_from_caller_to_op,
            encrypted_message_from_caller_to_caller
        ]

        self.log(b'\n ~~~ \n'.join(MSG_PIECES))
        MSG = BSEP.join(MSG_PIECES)
        self.log('MSG',MSG)
        MSG_b64 = b64encode(MSG)
        self.log(b' ~~~ ring ring ~~~ rriing ~~~',MSG_b64)

        msg_b64_str = MSG_b64.decode()
        self.log(b' ~~~ rirrrrng ring ~~~~  ring ~~ rrrrriing ~~~',msg_b64_str)

        ## escape slashes
        msg_b64_str_esc=msg_b64_str.replace('/','_')
        

        return msg_b64_str_esc

    
    def answer_phone(self,data_b64_str_esc, from_phone=None,to_phone=None):        
        ## escape slashes
        data_b64_s=data_b64_str_esc.replace('_','/')

        self.log('Pronto!\n ... '+data_b64_s+' ...?')

        # if not isBase64(data_b64_s):
            # self.log('incoming data not b64')
            # return OPERATOR_INTERCEPT_MESSAGE

        # string -> b64 bytes
        data_b64_b = data_b64_s.encode()
        self.log('data_b64_b',data_b64_b)

        # b64 -> raw bytes
        data = b64decode(data_b64_b)
        self.log('data',data)

        # split
        self.log('BSEP count',data.count(BSEP))
        self.log(data.split(BSEP))
        assert data.count(BSEP) == 3
        (
            unencr_header,  # Tele.pubkey_encr|Op.pubkey_decr
            data_encr_phone2phone,
            data_encr_caller2phone,
            data_encr_caller2caller
        ) = data.split(BSEP)

        self.log('unencr_header',unencr_header)
        self.log('data_encr_phone2phone',data_encr_phone2phone)
        self.log('data_encr_caller2phone',data_encr_caller2phone)
        self.log('data_encr_caller2caller',data_encr_caller2caller)

        # set up
        DATA = {}

        # layer 1: unencr
        # get other keys from halfkeys
        # from_phone_pubkey,to_phone_pubkey = self.reassemble_nec_keys_using_header(unencr_header)
        if not from_phone or not to_phone:
            from_phone,to_phone = self.discover_which_phones_from_header(unencr_header)


        self.log(f'I am {to_phone} and I am answering the phone! from {from_phone}')
        
        # layer 2: I know I (either Telephone or Operator) am the recipient of this msg
        from_phone_keychain = from_phone.keychain()
        from_phone_pubkey=from_phone_keychain.get('pubkey')
        to_phone_keychain = to_phone.keychain()
        to_phone_privkey=to_phone_keychain.get('privkey')

        self.log('data_encr_phone2phone',data_encr_phone2phone)
        self.log('from_phone_pubkey',from_phone_pubkey,from_phone)
        self.log('to_phone_privkey',to_phone_privkey,to_phone)

        # 2) decrypt from phone
        data_phone2phone = self.decrypt_from_send(
            msg_encr=data_encr_phone2phone,
            from_pubkey=from_phone_pubkey,
            to_privkey=to_phone_privkey
        )
        self.log('data_phone2phone',data_phone2phone)

        # 3) decrypt from caller
        from_caller_pubkey = self.reassemble_necessary_keys_using_decr_phone_data(data_phone2phone)
        data_caller2phone = self.decrypt_from_send(
            msg_encr=data_encr_caller2phone,
            from_pubkey=from_caller_pubkey,
            to_privkey=to_phone_privkey
        )
        self.log('data_caller2phone',data_caller2phone)


        # @TODO: 4) Caller 2 Caller
        #to_caller_pubkey = self.reassemble_necessary_keys_using_decr_caller_data(data_caller2phone)
        # send this to caller...


        DATA = {}
        dict_merge(DATA,data_phone2phone)
        dict_merge(DATA,data_caller2phone)
        # dict_merge(DATA,data_caller2caller)
        # dict_merge(DATA,data_by_caller)
        self.log('DATA!!!!!',DATA)
        return DATA





    # def encrypt_outgoing(self,
    #                     data_from_sender1={},
    #                     data_from_sender2={},
    #                     privkey_from_sender1=None,
    #                     privkey_from_sender2=None,
    #                     to_pubkey=None,
    #                     unencr_header=b''):
        
        
    #     # 2) encrypt to phone
    #     json_phone_encr = self.encrypt_to_send(data_from_sender1,from_phone_privkey,to_pubkey)
    #     self.log('json_phone_encr',json_phone_encr)

    #     # 3) to caller
    #     json_caller_encr = self.encrypt_to_send(json_caller,from_caller_privkey,to_pubkey)
    #     self.log()

    #     # return
    #     req_data_encr = unencr_header + BSEP + json_phone_encr + BSEP + json_caller_encr
    #     return req_data_encr

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

    def discover_which_phones_from_header(self,unencr_header):
        assert unencr_header.count(BSEP2)==1
        from_phone_pubkey_encr,to_phone_pubkey_decr = unencr_header.split(BSEP2)
        
        phone_keychain = self.phone.keychain()
        op_keychain = self.op.keychain()
        op_pubkey_encr = op_keychain.get('pubkey_encr')
        op_pubkey_decr = op_keychain.get('pubkey_decr')
        phone_pubkey_encr = phone_keychain.get('pubkey_encr')
        phone_pubkey_decr = phone_keychain.get('pubkey_encr')

        self.log('phone_keychain',phone_keychain)
        self.log('op_keychain',op_keychain)
        self.log('op_pubkey_encr',op_pubkey_encr)
        self.log('op_pubkey_decr',op_pubkey_decr)
        self.log('phone_pubkey_encr',phone_pubkey_encr)
        self.log('phone_pubkey_decr',phone_pubkey_decr)

        # was this sent from Phone -> Op?
        to_phone=None
        from_phone=None

        op_fits_as_to_phone=False
        tele_fits_as_to_phone=False
        op_fits_as_from_phone=False
        tele_fits_as_from_phone=False

        if op_pubkey_encr:
            op_fits_as_to_phone = self.assemble_key(op_pubkey_encr,to_phone_pubkey_decr)
            self.log('op_fits_as_to_phone',op_fits_as_to_phone)
            return (self.phone,self.op)
        if phone_pubkey_encr:
            tele_fits_as_to_phone = self.assemble_key(phone_pubkey_encr,to_phone_pubkey_decr)
            self.log('tele_fits_as_to_phone',tele_fits_as_to_phone)
            return (self.op,self.phone)
        if op_pubkey_decr:
            op_fits_as_from_phone = self.assemble_key(from_phone_pubkey_encr, op_pubkey_decr)
            self.log('op_fits_as_from_phone',op_fits_as_from_phone)
            return (self.op,self.phone)
        if phone_pubkey_decr:
            tele_fits_as_from_phone = self.assemble_key(from_phone_pubkey_encr,phone_pubkey_decr)
            self.log('tele_fits_as_from_phone',tele_fits_as_from_phone)
            return (self.phone,self.op)
        
        


        # # get phone pubkey
        # new_phone_keychain = self.phone.keychain(extra_keys={'pubkey_encr':phone_pubkey_encr},force=True)
        # new_op_keychain = self.keychain(extra_keys={'pubkey_decr':op_pubkey_decr},force=True)

        # phone_pubkey = new_phone_keychain.get('pubkey')
        # op_pubkey = new_op_keychain.get('pubkey')

        # self.log('reassembled phone/op pubkeys:',phone_pubkey,op_pubkey)
        # return (phone_pubkey,op_pubkey)


    def reassemble_necessary_keys_using_decr_phone_data(self,decr_phone_data):
        name=decr_phone_data.get('name')
        if not name: return None

        try:
            caller = Caller(name)
            self.log('got caller on phone',name,caller)
            return caller.pubkey_
        except:
            return

        
    





### CREATE PRIME ENTITIES
def create_phonelines():
    ## CREATE OPERATOR
    op = Operator(name=OPERATOR_NAME)
    op_keys_to_keep_on_client = ['pubkey']  # kept on app, stored under name
    op_keys_to_keep_on_3rdparty = ['privkey_decr']  # kept on .onion site
    op_keys_to_keep_on_server = ['pubkey',   # stored under name
                                'privkey_encr',
                                'adminkey_encr',
                                'adminkey_decr_encr',
                                'adminkey_decr_decr']   # kept on op server

    ## create phone
    phone = Operator(name=TELEPHONE_NAME)
    phone_keys_to_keep_on_client = ['pubkey','privkey_encr'] # kept on app; need both to init connection 
    phone_keys_to_keep_on_3rdparty = ['privkey_decr']  # dl by phone
    phone_keys_to_keep_on_server = ['pubkey']  # kept on op server

    # create keys for Op
    op_uri,op_decr_keys = op.forge_new_keys(
        keys_to_save=op_keys_to_keep_on_server,
        keys_to_return=op_keys_to_keep_on_client + op_keys_to_keep_on_3rdparty # on clients only
    )

    # create keys for phone
    phone_uri,phone_decr_keys = phone.forge_new_keys(
        name=TELEPHONE_NAME,
        keys_to_save=phone_keys_to_keep_on_server,  # on server only
        keys_to_return=phone_keys_to_keep_on_client + phone_keys_to_keep_on_3rdparty   # on clients only
    )

    # store URIs
    # op.save_uri_as_qrcode(odir=PATH_OPERATOR_WEB_CONTACTS_DIR)
    # op.save_uri_as_qrcode()
    
    # phone.save_uri_as_qrcode(odir=PATH_OPERATOR_WEB_CONTACTS_DIR)
    # phone.save_uri_as_qrcode()

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
    THIRD_PARTY_totalpkg = b64encode(omega_key.data + BSEP + THIRD_PARTY_DICT_pkg)

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
    
    pkg = r.text
    print('got from onion:',pkg)
    pkg = b64decode(pkg)
    print('got from onion:',pkg)

    OMEGA_KEY_b,remote_builtin_keychain_encr = pkg.split(BSEP)
    print('OMEGA_KEY_b',OMEGA_KEY_b)
    print('remote_builtin_keychain_encr',remote_builtin_keychain_encr)
    

    OMEGA_KEY = KomradeSymmetricKeyWithoutPassphrase(key=OMEGA_KEY_b)

    print('loaded Omega',OMEGA_KEY)
    remote_builtin_keychain = OMEGA_KEY.decrypt(remote_builtin_keychain_encr)
    
    print('remote_builtin_keychain',remote_builtin_keychain)
    
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
    
    print('>>>> loaded OPERATOR_KEYCHAIN',OPERATOR_KEYCHAIN)
    print('>>>> loaded TELEPHONE_KEYCHAIN',TELEPHONE_KEYCHAIN)
    stop
    return (OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN)

    # # load prime objects?
    # from komrade.backend.the_operator import TheOperator
    # from komrade.backend.the_telephone import TheTelephone
    # OPERATOR = TheOperator(keychain=OPERATOR_KEYCHAIN)
    # TELEPHONE = TheTelephone(keychain=TELEPHONE_KEYCHAIN)
    
    # return (OPERATOR,TELEPHONE)