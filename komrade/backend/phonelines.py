import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *





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
    op_res = op.forge_new_keys(
        keys_to_save=op_keys_to_keep_on_server,
        keys_to_return=op_keys_to_keep_on_client + op_keys_to_keep_on_3rdparty # on clients only
    )
    op_uri = op_res['uri_id']
    op_decr_keys = op_res['_keychain']
    
    #pring('op_uri',op_uri)
    #pring('op_decr_keys',op_decr_keys)

    # create keys for phone
    phone_res = phone.forge_new_keys(
        name=TELEPHONE_NAME,
        keys_to_save=phone_keys_to_keep_on_server,  # on server only
        keys_to_return=phone_keys_to_keep_on_client + phone_keys_to_keep_on_3rdparty   # on clients only
    )
    phone_uri = phone_res['uri_id']
    phone_decr_keys = phone_res['_keychain']

    #pring('phone_uri',phone_uri)
    #pring('phone_decr_keys',phone_decr_keys)

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

    #pring('THIRD_PARTY_DICT',THIRD_PARTY_DICT)

    # store local keys
    STORE_IN_APP = {OPERATOR_NAME:{}, TELEPHONE_NAME:{}}
    for key in op_keys_to_keep_on_client:
        if key in op_decr_keys:
            STORE_IN_APP[OPERATOR_NAME][key]=op_decr_keys[key]
    for key in phone_keys_to_keep_on_client:
        if key in phone_decr_keys:
            STORE_IN_APP[TELEPHONE_NAME][key]=phone_decr_keys[key]
    #pring('STORE_IN_APP',STORE_IN_APP)

    # package
    STORE_IN_APP_pkg = package_for_transmission(STORE_IN_APP) #package_for_transmission(STORE_IN_APP[TELEPHONE_NAME]) + BSEP + package_for_transmission(STORE_IN_APP[OPERATOR_NAME])
    THIRD_PARTY_DICT_pkg = package_for_transmission(THIRD_PARTY_DICT) #package_for_transmission(THIRD_PARTY_DICT[TELEPHONE_NAME]) + BSEP + package_for_transmission(THIRD_PARTY_DICT[OPERATOR_NAME])
    #pring('THIRD_PARTY_DICT_pkg',THIRD_PARTY_DICT_pkg)
    #pring('THIRD_PARTY_DICT_pkg',THIRD_PARTY_DICT_pkg)


    # encrypt
    omega_key = KomradeSymmetricKeyWithoutPassphrase()
    STORE_IN_APP_encr = b64encode(omega_key.encrypt(STORE_IN_APP_pkg))
    #pring('STORE_IN_APP_encr',STORE_IN_APP_encr)

    THIRD_PARTY_totalpkg = b64encode(omega_key.data + BSEP + omega_key.encrypt(THIRD_PARTY_DICT_pkg))
    #pring('THIRD_PARTY_totalpkg',THIRD_PARTY_totalpkg)

    # save
    with open(PATH_BUILTIN_KEYCHAIN,'wb') as of:
        of.write(STORE_IN_APP_encr)
        #pring('STORE_IN_APP_encr',STORE_IN_APP_encr)
        
    with open(PATH_OPERATOR_WEB_KEYS_FILE,'wb') as of:
        of.write(THIRD_PARTY_totalpkg)
        #pring('THIRD_PARTY_DICT_encr',THIRD_PARTY_totalpkg)


def connect_phonelines():
    # globals
    global OMEGA_KEY,OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN
    if OMEGA_KEY and OPERATOR_KEYCHAIN and TELEPHONE_KEYCHAIN:
        return (OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN,OMEGA_KEY)

    #pring('\n\n\n\nCONNECTING PHONELINES!\n\n\n\n')

    # import
    from komrade.backend.mazes import tor_request
    from komrade.backend import PATH_OPERATOR_WEB_KEYS_URL

    # load local keys
    if not os.path.exists(PATH_BUILTIN_KEYCHAIN):
        #pring('builtin keys not present??')
        return
    with open(PATH_BUILTIN_KEYCHAIN,'rb') as f:
        local_builtin_keychain_encr = b64decode(f.read())

    # load remote keys
    #pring('??',PATH_OPERATOR_WEB_KEYS_URL)
    r = komrade_request(PATH_OPERATOR_WEB_KEYS_URL)
    if r.status_code!=200:
        #pring('cannot authenticate the keymakers')
        return

    # unpack remote pkg
    
    pkg = r.text
    #pring('got from onion:',pkg)
    pkg = b64decode(pkg)
    #pring('got from onion:',pkg)

    OMEGA_KEY_b,remote_builtin_keychain_encr = pkg.split(BSEP)
    #pring('OMEGA_KEY_b',OMEGA_KEY_b)
    #pring('remote_builtin_keychain_encr',remote_builtin_keychain_encr)
    

    OMEGA_KEY = KomradeSymmetricKeyWithoutPassphrase(key=OMEGA_KEY_b)

    #pring('loaded Omega',OMEGA_KEY)
    # from komrade.utils import unpackage_from_transmission
    remote_builtin_keychain = unpackage_from_transmission(OMEGA_KEY.decrypt(remote_builtin_keychain_encr))
    #pring('remote_builtin_keychain',remote_builtin_keychain)
    
    remote_builtin_keychain_phone_json,remote_builtin_keychain_op_json = remote_builtin_keychain[TELEPHONE_NAME],remote_builtin_keychain[OPERATOR_NAME]
    #pring('remote_builtin_keychain_phone_json',remote_builtin_keychain_phone_json)
    #pring('remote_builtin_keychain_op_json',remote_builtin_keychain_op_json)
    
    # unpack local pkg
    local_builtin_keychain = unpackage_from_transmission(OMEGA_KEY.decrypt(local_builtin_keychain_encr))
    #pring('local_builtin_keychain',local_builtin_keychain)

    local_builtin_keychain_phone_json,local_builtin_keychain_op_json = local_builtin_keychain[TELEPHONE_NAME],local_builtin_keychain[OPERATOR_NAME]
    #pring('local_builtin_keychain_phone_json',local_builtin_keychain_phone_json)
    #pring('local_builtin_keychain_op_json',local_builtin_keychain_op_json)

    # set builtin keychains
    TELEPHONE_KEYCHAIN={}
    OPERATOR_KEYCHAIN={}
    dict_merge(TELEPHONE_KEYCHAIN,local_builtin_keychain_phone_json)
    dict_merge(OPERATOR_KEYCHAIN,local_builtin_keychain_op_json)
    dict_merge(TELEPHONE_KEYCHAIN,remote_builtin_keychain_phone_json)
    dict_merge(OPERATOR_KEYCHAIN,remote_builtin_keychain_op_json)
    
    # #pring('>>>> loaded OPERATOR_KEYCHAIN',OPERATOR_KEYCHAIN)
    # #pring('>>>> loaded TELEPHONE_KEYCHAIN',TELEPHONE_KEYCHAIN)
    return (OPERATOR_KEYCHAIN,TELEPHONE_KEYCHAIN,OMEGA_KEY)
