import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from comrad import *
from comrad.backend import *




def create_phonelines():
    # crypt
    keycrypt = Crypt(fn=PATH_CRYPT_OP_KEYS)
    # print(keycrypt.fn)

    # Operator
    op_keypair = ComradAsymmetricKey()
    op_pubkey,op_privkey = op_keypair.pubkey_obj,op_keypair.privkey_obj
    op_uri = op_pubkey.data_b64

    op_privkey_decr = ComradSymmetricKeyWithoutPassphrase()
    op_privkey_encr = ComradEncryptedAsymmetricPrivateKey(
        data=op_privkey_decr.encrypt(op_privkey.data)
    )

    ## world
    world_keypair = ComradAsymmetricKey()
    world_pubkey,world_privkey = world_keypair.pubkey_obj,world_keypair.privkey_obj
    world_uri = world_pubkey.data_b64
    world_privkey_decr = ComradSymmetricKeyWithoutPassphrase()
    world_privkey_encr = ComradEncryptedAsymmetricPrivateKey(
        data=world_privkey_decr.encrypt(world_privkey.data)
    )

    keycrypt.set(OPERATOR_NAME,op_pubkey.data,prefix='/pubkey/')
    keycrypt.set(op_uri,OPERATOR_NAME,prefix='/name/')
    
    op_world_pkg = [
        op_privkey_decr.data,
        op_privkey_encr.data,
        world_privkey_decr.data,
        world_privkey_encr.data
    ]
    
    with open(PATH_SUPER_SECRET_OP_KEY,'wb') as of:
        of.write(b64enc(BSEP.join(op_world_pkg)))
    with open(PATH_OPERATOR_WEB_KEYS_FILE,'w') as of:
        of.write(op_pubkey.data_b64_s)

    ## Telephone
    phone_keypair = ComradAsymmetricKey()
    phone_pubkey,phone_privkey = phone_keypair.pubkey_obj,phone_keypair.privkey_obj
    phone_uri = phone_pubkey.data_b64
    keycrypt.set(TELEPHONE_NAME,phone_pubkey.data,prefix='/pubkey/')
    keycrypt.set(phone_uri,TELEPHONE_NAME,prefix='/name/')

    

    

    keycrypt.set(WORLD_NAME,world_pubkey.data,prefix='/pubkey/')
    keycrypt.set(world_uri,WORLD_NAME,prefix='/name/')
    # keycrypt.set(world_uri,world_privkey.data,prefix='/privkey/')
    #keycrypt.set(world_uri,world_privkey_encr.data,prefix='/privkey_encr/')
    #keycrypt.set(world_uri,world_privkey_decr.data,prefix='/privkey_decr/')




    # keys to save built in
    builtin_keys = {
        OPERATOR_NAME: {
            'pubkey':op_pubkey.data,
        },
        TELEPHONE_NAME: {
            'pubkey':phone_pubkey.data,
            'privkey':phone_privkey.data,
        },
        WORLD_NAME: {
            'pubkey':world_pubkey.data,
        }
    }

    import pickle
    from base64 import b64encode
    builtin_keys_b = pickle.dumps(builtin_keys)

    # omega_key = ComradSymmetricKeyWithoutPassphrase()
    # builtin_keys_b_encr = omega_key.encrypt(builtin_keys_b)
    # builtin_keys_b_encr_with_key = omega_key.data + BSEP + builtin_keys_b_encr
    # builtin_keys_b_encr_with_key_b64 = b64encode(builtin_keys_b_encr_with_key)
    builtin_keys_b64 = b64encode(builtin_keys_b)

    with open(PATH_BUILTIN_KEYCHAIN,'wb') as of:
        of.write(builtin_keys_b64)
        # of.write(builtin_keys_b_encr_with_key_b64)
        print('>> saved:',PATH_BUILTIN_KEYCHAIN)
        # print(builtin_keys_b_encr_with_key_b64)
        print(builtin_keys_b64)


















def check_phonelines():
    # if needed
    create_secret()

    # is world there?
    keycrypt = Crypt(fn=PATH_CRYPT_OP_KEYS)
    
    # builtins
    with open(PATH_BUILTIN_KEYCHAIN,'rb') as f:        
        # builtin_keys_encr_b64 = f.read()
        builtin_keys_b64 = f.read()
    # builtin_keys_encr = b64decode(builtin_keys_encr_b64)
    # omega_key_b,builtin_keys_encr = builtin_keys_encr.split(BSEP)
    # omega_key = ComradSymmetricKeyWithoutPassphrase(omega_key_b)
    # builtin_keys_b = omega_key.decrypt(builtin_keys_encr)
    builtin_keys = pickle.loads(b64decode(builtin_keys_b64))
    # print(builtin_keys)

    for name in builtin_keys:
        pubkey=builtin_keys[name]['pubkey']
        uri_id=b64encode(pubkey)
        # print(name,pubkey,uri_id)
        keycrypt.set(
            uri_id.decode(),
            name,
            prefix=f'/name/',override=True
        )
        for keyname,keyval in builtin_keys[name].items():
            uri=name if keyname=='pubkey' else uri_id
            keycrypt.set(
                uri,
                keyval,
                prefix=f'/{keyname}/',override=True
            )

    # make sure world's qr is there too
    ofnfn = os.path.join(PATH_QRCODES,WORLD_NAME+'.png')
    if not os.path.exists(ofnfn):
        world_uri = b64encode(builtin_keys[WORLD_NAME]['pubkey'])  
        import pyqrcode
        qr = pyqrcode.create(world_uri)
        qr.png(ofnfn,scale=5)
        #print('>> saved:',ofnfn)


    return builtin_keys


def test_phonelines():
    from comrad.backend.the_telephone import TheTelephone
    from comrad.backend.the_operator import TheOperator
    from getpass import getpass
    phone = TheTelephone()
    op = TheOperator(passphrase=getpass())

    print('phone',dict_format(phone.keychain()))
    print('op',dict_format(op.keychain()))

    print(op.privkey)

if __name__ == '__main__':
    test_phonelines()