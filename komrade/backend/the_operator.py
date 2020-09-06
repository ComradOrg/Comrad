"""
There is only one operator!
Running on node prime.
"""
# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *



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
        KEYCHAIN = self.keychain(allow_builtin=False,force=True)
        self.log('as of now 1, I the operator have these keys:',KEYCHAIN.keys())
        # stop1
        PHONE_PUBKEY=None
        MY_PRIVKEY=None
        
        if data_unencr:
            self.log('unencrypted data:',data_unencr)
            
            if BSEP2 in data_unencr:
                my_privkey_decr,phone_pubkey_decr = data_unencr.split(BSEP2)
                self.log('my_privkey_decr',my_privkey_decr)
                self.log('phone_pubkey_decr',phone_pubkey_decr)

                # get phone pubkey
                new_phone_keychain = self.phone.keychain(extra_keys={'pubkey_decr':phone_pubkey_decr})
                new_op_keychain = self.keychain(extra_keys={'privkey_decr':my_privkey_decr})

                PHONE_PUBKEY = new_phone_keychain.get('pubkey')
                MY_PRIVKEY = new_op_keychain.get('privkey')

                self.log('PHONE_PUBKEY',PHONE_PUBKEY)
                self.log('MY_PRIVKEY',MY_PRIVKEY)
                stopppp
                


        if DATA.get('_keychain'):
            DATA['_keychain'] = self.valid_keychain(DATA['_keychain'])
            # self.log('found keys in unencrypted data:',DATA['_keychain'])
            # stop2

            KEYCHAIN = self.keychain(allow_builtin=False,force=True,extra_keys=DATA['_keychain'])
            self.log('as of now 2, I the operator have these keys:',KEYCHAIN.keys())
            # stopppppppp
        self.log('DATA as of now!?',DATA)
        # stop

        if data_encr_by_phone:
            
            # then try to unwrap telephone encryption
            me_privkey = KEYCHAIN.get('privkey')  #self.privkey(keychain = DATA.get('_keychain',{}))
            if not me_privkey:
                self.log('!! could not assemble my private key. failing.')
                return OPERATOR_INTERCEPT_MESSAGE
            
            # self.log('as of now 3, I the operator have these keys:',self.keychain().keys())
            self.log('me_privkey now',me_privkey)
            # print(me_privkey, '<--',them_pubkey)
            try:
                data_unencr_by_phone = SMessage(me_privkey, self.phone.pubkey_).unwrap(data_encr_by_phone)
                self.log('decrypted data !!!:',data_unencr_by_phone)
            except ThemisError as e:
                self.log('not really from the telephone?',e)
                return OPERATOR_INTERCEPT_MESSAGE
            
            data_unencr_by_phone_json = json.loads(data_unencr_by_phone.decode())
            self.log('data_unencr_by_phone_json',data_unencr_by_phone_json)
            if type(data_unencr_by_phone_json)== dict:
                dict_merge(DATA, data_unencr_by_phone_json)

        self.log('DATA as of now 3!?',DATA)
        stop3

        if data_encr_by_caller and 'name' in data_unencr_by_phone:
            name=data_unencr_by_phone['name']
            keychain=data_unencr_by_phone.get('_keychain',{})

            # decrypt using this user's pubkey on record
            caller = Caller(name)
            data_unencr2 = SMessage(self.privkey_, caller.pubkey_).unwrap(data_encr_by_caller)

            if type(data_unencr_by_phone)==dict and type(data_encr_by_caller)==dict:
                data = data_unencr_by_phone
                dict_merge(data_encr_by_caller, data)
            else:
                data=(data_unencr_by_phone,data_encr_by_caller)
        else:
            data = data_unencr_by_phone
        return data

    def receive(self,data):
        # decrypt
        data = self.decrypt_incoming(data)

        # decode
        data_s = data.decode()
        data_json = json.loads(data_s)


        self.log('DATA =',type(data),data)
        self.log('DATA_s =',type(data_s),data_s)
        self.log('DATA_json =',type(data_json),data_s)
        
        return self.route(data_json)

    def route(self, data):
        # data = self.decrypt_incoming(data)
        # self.log('DATA =',data)
        return data# 'success!'


def init_operators():
    op = TheOperator()
    phone = TheTelephone()

    op_decr_keys = op.forge_new_keys(
        keys_to_save=['pubkey','privkey_encr','adminkey_encr','adminkey_decr_encr','adminkey_decr_decr'],
        keys_to_return=['pubkey','privkey_decr']
    )

    phone_decr_keys = phone.forge_new_keys(
        keys_to_save=['pubkey_encr'],
        keys_to_return=['pubkey_decr','privkey']
    )

    print('\n'*5)
    print('OPERATOR_KEYCHAIN =',op_decr_keys)
    print()
    print('TELEPHONE_KEYCHAIN =',phone_decr_keys)

    # stringify
    for k,v in phone_decr_keys.items():
        v_s = b64encode(v).decode('utf-8')
        phone_decr_keys[k]=v_s
    for k,v in op_decr_keys.items():
        v_s = b64encode(v).decode('utf-8')
        op_decr_keys[k]=v_s


    # print('total_d',total_d)
    builtin_keychains = {OPERATOR_NAME:op_decr_keys, TELEPHONE_NAME:phone_decr_keys}
    builtin_keychains_s = json.dumps(builtin_keychains)

    print('builtin_keychains =',builtin_keychains)

    print('builtin_keychains_s =',builtin_keychains_s)
    builtin_keychains_b = builtin_keychains_s.encode('utf-8')
    
    builtin_keychains_b_decr = KomradeSymmetricKeyWithoutPassphrase()
    builtin_keychains_b_encr = builtin_keychains_b_decr.encrypt(builtin_keychains_b)

    builtin_keychains_b_decr_b64 = b64encode(builtin_keychains_b_decr.key)
    builtin_keychains_b_encr_b64 = b64encode(builtin_keychains_b_encr) 

    with open(PATH_BUILTIN_KEYCHAINS_ENCR,'wb') as of:
        of.write(builtin_keychains_b_encr_b64)
        print('>> saved:',PATH_BUILTIN_KEYCHAINS_ENCR)
        print(builtin_keychains_b_encr_b64,'\n\n')
    with open(PATH_BUILTIN_KEYCHAINS_DECR,'wb') as of:
        of.write(builtin_keychains_b_decr_b64)
        print('>> saved:',PATH_BUILTIN_KEYCHAINS_DECR)
        print(builtin_keychains_b_decr_b64,'\n')
        


    # op_pub = op.pubkey_decr_
    # phone_pub = phone.pubkey_decr_
    # phone_priv = phone.privkey_decr_

    # print('OPERATOR_PUBKEY_DECR =',b64encode(op_pub))
    # print('TELEPHONE_PUBKEY_DECR =',b64encode(phone_pub))
    # print('TELEPHONE_PRIVKEY_DECR =',b64encode(phone_priv))
    # return {
        # 'op.keychain()':op.keychain(),
        # 'phone.keychain()':phone.keychain()
    # }


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