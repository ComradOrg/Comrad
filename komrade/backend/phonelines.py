import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *




def create_phonelines():
    # crypt
    keycrypt = Crypt(fn=PATH_CRYPT_OP_KEYS)

    # Operator
    op_keypair = KomradeAsymmetricKey()
    op_pubkey,op_privkey = op_keypair.pubkey_obj,op_keypair.privkey_obj
    op_privkey_decr = KomradeSymmetricKeyWithPassphrase()
    op_privkey_encr_b = op_privkey_decr.encrypt(op_privkey.data)
    op_privkey_encr = KomradeEncryptedAsymmetricPrivateKey(op_privkey_encr_b)

    # save pub and priv
    op_uri = op_pubkey.data_b64
    keycrypt.set(OPERATOR_NAME,op_pubkey.data,prefix='/pubkey/')
    keycrypt.set(op_uri,op_privkey_encr.data,prefix='/privkey_encr/')
    

    ## Telephone
    phone_keypair = KomradeAsymmetricKey()
    phone_pubkey,phone_privkey = phone_keypair.pubkey_obj,phone_keypair.privkey_obj
    phone_privkey_decr = KomradeSymmetricKeyWithoutPassphrase()
    phone_privkey_encr_b = phone_privkey_decr.encrypt(phone_privkey.data)
    phone_privkey_encr = KomradeEncryptedAsymmetricPrivateKey(phone_privkey_encr_b)

    # save pub and priv
    keycrypt.set(TELEPHONE_NAME,phone_pubkey.data,prefix='/pubkey/')

    ## world
    world_keypair = KomradeAsymmetricKey()
    world_pubkey,world_privkey = world_keypair.pubkey_obj,world_keypair.privkey_obj
    world_privkey_decr = KomradeSymmetricKeyWithPassphrase()
    world_privkey_encr_b = world_privkey_decr.encrypt(world_privkey.data)
    world_privkey_encr = KomradeEncryptedAsymmetricPrivateKey(world_privkey_encr_b)

    # save pub and priv
    world_uri = world_pubkey.data_b64
    keycrypt.set(WORLD_NAME,world_pubkey.data,prefix='/pubkey/')
    keycrypt.set(world_uri,world_privkey_encr.data,prefix='/privkey_encr/')




    # keys to save built in
    builtin_keys = [
        {
            'name':OPERATOR_NAME,
            'pubkey':op_pubkey.data,
        },
        {
            'name':TELEPHONE_NAME,
            'pubkey':phone_pubkey.data,
            'privkey':phone_privkey.data,
        },
        {
            'name':WORLD_NAME,
            'pubkey':world_pubkey.data,
        }
    ]

    import pickle
    from base64 import b64encode
    builtin_keys_b = pickle.dumps(builtin_keys)

    omega_key = KomradeSymmetricKeyWithoutPassphrase()
    builtin_keys_b_encr = omega_key.encrypt(builtin_keys_b)
    builtin_keys_b_encr_with_key = omega_key.data + BSEP + builtin_keys_b_encr
    builtin_keys_b_encr_with_key_b64 = b64encode(builtin_keys_b_encr_with_key)

    with open(PATH_BUILTIN_KEYCHAIN,'wb') as of:
        of.write(builtin_keys_b_encr_with_key_b64)
        print('>> saved:',PATH_BUILTIN_KEYCHAIN)
        print(builtin_keys_b_encr_with_key_b64)














def create_secret():
    if not os.path.exists(PATH_CRYPT_SECRET):    
        secret = get_random_binary_id()
        from komrade.backend.keymaker import make_key_discreet
        print('shhh! creating secret:',make_key_discreet(secret))
        with open(PATH_CRYPT_SECRET,'wb') as of:
            of.write(secret)



def check_phonelines():
    # if needed
    create_secret()

    # is world there?
    keycrypt = Crypt(fn=PATH_CRYPT_OP_KEYS)
    
    # builtins
    with open(PATH_BUILTIN_KEYCHAIN,'rb') as f:        
        builtin_keys_encr_b64 = f.read()
    builtin_keys_encr = b64decode(builtin_keys_encr_b64)
    omega_key_b,builtin_keys_encr = builtin_keys_encr.split(BSEP)
    omega_key = KomradeSymmetricKeyWithoutPassphrase(omega_key_b)
    builtin_keys_b = omega_key.decrypt(builtin_keys_encr)
    builtin_keys = pickle.loads(builtin_keys_b)
    # print(builtin_keys)

    for keyring in builtin_keys:
        name = keyring.get('name')
        keychain = dict((k,v) for k,v in keyring.items() if k!='name')
        if not 'pubkey' in keyring: continue
        uri = b64encode(keychain.get('pubkey'))
        if not keycrypt.has(name,prefix='/pubkey/'):
            keycrypt.set(name,keychain['pubkey'],prefix='/pubkey/')
        for key in [k for k in keychain if k!='pubkey']:
            if not keycrypt.has(uri,prefix=f'/{key}/'):
                keycrypt.set(uri,keychain[key],prefix=f'/{key}/')

        # make sure world's qr is there too
        if name==WORLD_NAME:
            import pyqrcode
            qr = pyqrcode.create(uri)
            ofnfn = os.path.join(PATH_QRCODES,name+'.png')
            qr.png(ofnfn,scale=5)
            # print('>> saved:',ofnfn)


    return builtin_keys



# ### CREATE PRIME ENTITIES
# def create_phonelines1():
#     # create secret
#     create_secret()

#     ## CREATE OPERATOR
#     op = Keymaker(name=OPERATOR_NAME)
#     op_keys_to_keep_on_client = ['pubkey']  # kept on app, stored under name
#     op_keys_to_keep_on_3rdparty = []  # kept on .onion site
#     op_keys_to_keep_on_server = ['pubkey',   # stored under name
#                                 'privkey_encr']   # kept on op server

#     ## create phone
#     phone = Keymaker(name=TELEPHONE_NAME)
#     phone_keys_to_keep_on_client = ['pubkey','privkey_encr','privkey_decr'] # kept on app; need both to init connection 
#     phone_keys_to_keep_on_3rdparty = ['']  # dl by phone
#     phone_keys_to_keep_on_server = ['pubkey']  # kept on op server

#     ## create phone
#     world = Keymaker(name=WORLD_NAME)
#     world_keys_to_keep_on_client = ['pubkey','privkey_encr']
#     world_keys_to_keep_on_3rdparty = []
#     world_keys_to_keep_on_server = ['pubkey']


#     # key types
#     key_types = {
#         'pubkey':KomradeAsymmetricPublicKey,
#         'privkey':KomradeAsymmetricPrivateKey,
#         'privkey_encr':KomradeEncryptedAsymmetricPrivateKey,
#         'privkey_decr':KomradeSymmetricKeyWithoutPassphrase,
#         'adminkey':KomradeSymmetricKeyWithoutPassphrase,
#         'adminkey_encr':KomradeEncryptedSymmetricKey,
#         'adminkey_decr':KomradeSymmetricKeyWithPassphrase,
#     }

#     key_types_phone = {**key_types, **{'privkey_decr':KomradeSymmetricKeyWithoutPassphrase}}

#     print('!?!?!?!',key_types_phone)

#     # create keys for Op
#     op_decr_keys = op.forge_new_keys(
#         key_types=key_types,
#         keys_to_save=op_keys_to_keep_on_server,
#         keys_to_return=op_keys_to_keep_on_client + op_keys_to_keep_on_3rdparty # on clients only
        
#     )
#     #print('op!',op_uri)
#     print(op_decr_keys)
#     # exit()

#     # create keys for phone
#     phone_decr_keys = phone.forge_new_keys(
#         key_types=key_types_phone,
#         keys_to_save=phone_keys_to_keep_on_server,  # on server only
#         keys_to_return=phone_keys_to_keep_on_client + phone_keys_to_keep_on_3rdparty   # on clients only
#     )
#     #print('phone!',op_uri)
#     print(phone_decr_keys)

#     # create keys for world
#     world_decr_keys = world.forge_new_keys(
#         key_types=key_types,
#         keys_to_save=world_keys_to_keep_on_server,
#         keys_to_return=world_keys_to_keep_on_client + world_keys_to_keep_on_3rdparty # on clients only
#     )
#     #print('world!',op_uri)
#     print(world_decr_keys)
#     ## store remote keys
#     THIRD_PARTY_DICT = {OPERATOR_NAME:{}, TELEPHONE_NAME:{}, WORLD_NAME:{}}
#     for key in op_keys_to_keep_on_3rdparty:
#         if key in op_decr_keys:
#             THIRD_PARTY_DICT[OPERATOR_NAME][key]=op_decr_keys[key]
#     for key in phone_keys_to_keep_on_3rdparty:
#         if key in phone_decr_keys:
#             THIRD_PARTY_DICT[TELEPHONE_NAME][key]=phone_decr_keys[key]
#     for key in world_keys_to_keep_on_3rdparty:
#         if key in world_decr_keys:
#             THIRD_PARTY_DICT[WORLD_NAME][key]=world_decr_keys[key]

#     print('THIRD_PARTY_DICT',THIRD_PARTY_DICT)

#     # store local keys
#     STORE_IN_APP = {OPERATOR_NAME:{}, TELEPHONE_NAME:{}, WORLD_NAME:{}}
#     for key in op_keys_to_keep_on_client:
#         if key in op_decr_keys:
#             STORE_IN_APP[OPERATOR_NAME][key]=op_decr_keys[key]
#     for key in phone_keys_to_keep_on_client:
#         if key in phone_decr_keys:
#             STORE_IN_APP[TELEPHONE_NAME][key]=phone_decr_keys[key]
#     for key in world_keys_to_keep_on_client:
#         if key in world_decr_keys:
#             STORE_IN_APP[WORLD_NAME][key]=world_decr_keys[key]
#     print('STORE_IN_APP',STORE_IN_APP)

#     # package
#     import pickle
#     STORE_IN_APP_pkg = pickle.dumps(STORE_IN_APP) #pickle.dumps(STORE_IN_APP[TELEPHONE_NAME]) + BSEP + pickle.dumps(STORE_IN_APP[OPERATOR_NAME])
#     THIRD_PARTY_DICT_pkg = pickle.dumps(THIRD_PARTY_DICT) #pickle.dumps(THIRD_PARTY_DICT[TELEPHONE_NAME]) + BSEP + pickle.dumps(THIRD_PARTY_DICT[OPERATOR_NAME])

#     # encrypt
#     omega_key = KomradeSymmetricKeyWithoutPassphrase()
#     STORE_IN_APP_encr = b64encode(omega_key.encrypt(STORE_IN_APP_pkg))
#     THIRD_PARTY_totalpkg = b64encode(omega_key.data + BSEP + omega_key.encrypt(THIRD_PARTY_DICT_pkg))
#     #print('THIRD_PARTY_totalpkg',THIRD_PARTY_totalpkg)

#     # save
#     with open(PATH_BUILTIN_KEYCHAIN,'wb') as of:
#         of.write(STORE_IN_APP_encr)
#         #print('STORE_IN_APP_encr',STORE_IN_APP_encr)
        
#     with open(PATH_OPERATOR_WEB_KEYS_FILE,'wb') as of:
#         of.write(THIRD_PARTY_totalpkg)
#         #print('THIRD_PARTY_DICT_encr',THIRD_PARTY_totalpkg)


# def connect_phonelines():
#     # globals
#     global OMEGA_KEY,OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN,WORLD_KEYCHAIN
#     if OMEGA_KEY and OPERATOR_KEYCHAIN and TELEPHONE_KEYCHAIN and WORLD_KEYCHAIN:
#         return (OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN,WORLD_KEYCHAIN,OMEGA_KEY)

#     # import
#     from komrade.backend.mazes import tor_request
#     from komrade.backend import PATH_OPERATOR_WEB_KEYS_URL

#     # load remote keys
#     r = komrade_request(PATH_OPERATOR_WEB_KEYS_URL)
#     if r.status_code!=200:
#         # return
#         raise KomradeException('oh no!')
#     pkg = r.text
#     pkg = b64decode(pkg)
#     OMEGA_KEY_b,remote_builtin_keychain_encr = pkg.split(BSEP)
#     OMEGA_KEY = KomradeSymmetricKeyWithoutPassphrase(key=OMEGA_KEY_b)
#     remote_builtin_keychain = pickle.loads(OMEGA_KEY.decrypt(remote_builtin_keychain_encr))
#     (
#         remote_builtin_keychain_phone_json,
#         remote_builtin_keychain_op_json,
#         remote_builtin_keychain_world_json
#     ) = (
#         remote_builtin_keychain[TELEPHONE_NAME],
#         remote_builtin_keychain[OPERATOR_NAME],
#         remote_builtin_keychain[WORLD_NAME]
#     )
#     #print('remote!',
#     #     remote_builtin_keychain_phone_json,
#     #     remote_builtin_keychain_op_json,
#     #     remote_builtin_keychain_world_json
#     # #)

#     # load local keys
#     if not os.path.exists(PATH_BUILTIN_KEYCHAIN):
#         return
#     with open(PATH_BUILTIN_KEYCHAIN,'rb') as f:
#         local_builtin_keychain_encr = b64decode(f.read())
#     local_builtin_keychain = pickle.loads(OMEGA_KEY.decrypt(local_builtin_keychain_encr))
#     (
#         local_builtin_keychain_phone_json,
#         local_builtin_keychain_op_json,
#         local_builtin_keychain_world_json
#     ) = (local_builtin_keychain[TELEPHONE_NAME],
#         local_builtin_keychain[OPERATOR_NAME],
#         local_builtin_keychain[WORLD_NAME]
#     )
#     #print('local!',
#     #     local_builtin_keychain_phone_json,
#     #     local_builtin_keychain_op_json,
#     #     local_builtin_keychain_world_json
#     # )



#     # set builtin keychains
#     TELEPHONE_KEYCHAIN={}
#     OPERATOR_KEYCHAIN={}
#     WORLD_KEYCHAIN={}
#     dict_merge(TELEPHONE_KEYCHAIN,local_builtin_keychain_phone_json)
#     dict_merge(OPERATOR_KEYCHAIN,local_builtin_keychain_op_json)
#     dict_merge(WORLD_KEYCHAIN,local_builtin_keychain_world_json)
#     dict_merge(TELEPHONE_KEYCHAIN,remote_builtin_keychain_phone_json)
#     dict_merge(OPERATOR_KEYCHAIN,remote_builtin_keychain_op_json)
#     dict_merge(WORLD_KEYCHAIN,remote_builtin_keychain_world_json)

#     # @hack: make sure world saved as contact?
#     ofnfn=os.path.join(PATH_QRCODES,WORLD_NAME+'.png')
#     if not os.path.exists(ofnfn):
#         import pyqrcode    
#         uri_id = b64encode(WORLD_KEYCHAIN['pubkey'])
#         qr = pyqrcode.create(uri_id)
#         qr.png(ofnfn,scale=5)
#         qr_str = qr.terminal()
#         #print(f'Saved world to QR:\n{qr_str}')
    
#     # ##print('>>>> loaded OPERATOR_KEYCHAIN',OPERATOR_KEYCHAIN)
#     # ##print('>>>> loaded TELEPHONE_KEYCHAIN',TELEPHONE_KEYCHAIN)
#     return (OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN,WORLD_KEYCHAIN,OMEGA_KEY)

def test_phonelines():
    from komrade.backend.the_telephone import TheTelephone
    from komrade.backend.the_operator import TheOperator

    phone = TheTelephone()
    op = TheOperator()

    print('phone',dict_format(phone.keychain()))
    print('op',dict_format(op.keychain()))


if __name__ == '__main__':
    test_phonelines()