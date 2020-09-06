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
    The remote operator! Only one!
    """
    

    def __init__(self, name = OPERATOR_NAME, passphrase='acc'):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """
        # init req paths
        # if not os.path.exists(PATH_OPERATOR): os.makedirs(PATH_OPERATOR)
        if not passphrase:
            passphrase=getpass.getpass('Hello, this is the Operator speaking. What is the passphrase?\n> ')
        super().__init__(name,passphrase)

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

    def route(self, data):
        data = self.decrypt_incoming(data)
        self.log('DATA =',data)
        return 'success!'


def init_operators():
    op = Operator(
        name=OPERATOR_NAME,
        path_crypt_keys=PATH_CRYPT_OP_KEYS,
        path_crypt_data=PATH_CRYPT_OP_DATA
    )

    phone = Operator(
        name=TELEPHONE_NAME,
        path_crypt_keys=PATH_CRYPT_CA_KEYS,
        path_crypt_data=PATH_CRYPT_CA_DATA
    )

    op.get_new_keys()
    phone.get_new_keys()

    #op_pub = op.pubkey_
    #phone_pub = phone.pubkey_
    #phone_priv = phone.privkey_

    #print('OPERATOR_PUBKEY =',b64encode(op_pub))
    #print('TELEPHONE_PUBKEY =',b64encode(phone_pub))
    #print('TELEPHONE_PRIVKEY =',b64encode(phone_priv))
    return {
        'op.keychain()':op.keychain(),
        'phone.keychain()':phone.keychain()
    }


def test_op():
    op = TheOperator()
    #op.boot()
    #pubkey = op.keychain()['pubkey']
    #pubkey_b64 = b64encode(pubkey)
    #print(pubkey_b64)
    keychain = op.keychain(force=True)
    from pprint import pprint
    pprint(keychain)
    
    pubkey = op.keychain()['pubkey']
    pubkey_b64 = b64encode(pubkey)
    print(pubkey)

if __name__ == '__main__': test_op()