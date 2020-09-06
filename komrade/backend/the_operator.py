"""
There is only one operator!
Running on node prime.
"""
# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *
from komrade.backend.operators import *
from komrade.backend.mazes import *



class TheOperator(Operator):
    """
    The remote operator
    """
    

    def __init__(self, name = OPERATOR_NAME, passphrase='acc'):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """
        # init req paths
        # if not os.path.exists(PATH_OPERATOR): os.makedirs(PATH_OPERATOR)
        if not passphrase:
            passphrase=getpass.getpass('Hello, this is the Operator speaking. What is the passphrase?\n> ')
        super().__init__(name,passphrase,path_crypt_keys=PATH_CRYPT_OP_KEYS,path_crypt_data=PATH_CRYPT_OP_DATA)


    def decrypt_incoming(self,data):
        # step 1 split:
        data_unencr,data_encr = data.split(BSEP)
        self.log('data_unencr =',data_unencr)
        self.log('data_encr =',data_encr)
        if data_encr and 'name' in data_unencr:
            name=data_unencr['name']
            keychain=data_unencr.get('keychain',{})

            # decrypt using this user's pubkey on record
            caller = Operator(name)
            from_pubkey = user.pubkey(keychain=keychain)
            data_unencr2 = SMessage(OPERATOR.privkey_, from_pubkey).unwrap(data_encr)

            if type(data_unencr)==dict and type(data_unencr2)==dict:
                data = data_unencr
                dict_merge(data_unencr2, data)
            else:
                data=(data_unencr,data_unencr2)
        else:
            data = data_unencr
        return data

    def receive(self,data):
        # decrypt
        data = self.decrypt_incoming(data)

        # decode
        data_s = data.decode()


        self.log('DATA =',data_s)
        stop
        return self.route(data)

    def route(self, data):
        # data = self.decrypt_incoming(data)
        # self.log('DATA =',data)
        return data# 'success!'


def init_operators():
    op = Operator(
        name=OPERATOR_NAME,
        path_crypt_keys=PATH_CRYPT_OP_KEYS,
        path_crypt_data=PATH_CRYPT_OP_DATA
    )

    phone = Operator(
        name=TELEPHONE_NAME,
        path_crypt_keys=PATH_CRYPT_OP_KEYS,
        path_crypt_data=PATH_CRYPT_OP_KEYS
    )


    # keys_to_return = [k for k in KEYMAKER_DEFAULT_KEYS_TO_RETURN if not k.startswith('admin')]
    
    # for the root entities, the *users* keep the encrypted version,
    # and the Op and Telephone just have decryptor keys
    # keys_to_save = ['pubkey_decr','privkey_decr','adminkey_decr_decr']
    
    # keys_to_save = ['pubkey_encr','privkey_encr','adminkey_decr_encr','adminkey_decr_decr','adminkey_encr']
    # keys_to_return = ['pubkey_decr','privkey_decr']

    # keys_to_return = ['pubkey_encr','privkey_encr','adminkey_encr','adminkey_decr_encr']
    op_decr_keys = op.forge_new_keys(
        keys_to_save=['pubkey','privkey','adminkey_encr','adminkey_decr_encr','adminkey_decr_decr'],
        keys_to_return=['pubkey']
    )

    phone_decr_keys = phone.forge_new_keys(
        keys_to_save=['pubkey'],
        keys_to_return=['pubkey','privkey']
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