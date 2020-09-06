# addresses
KOMRADE_URL = 'komrade.app'
KOMRADE_ONION = 'u7spnj3dmwumzoa4.onion'
KOMRADE_ONION2 = 'rwg4zcnpwshv4laq.onion' #'128.232.229.63' #'komrade.app'


OPERATOR_API_URL = f'http://{KOMRADE_ONION}/op/'


# paths
import os
PATH_KOMRADE = os.path.abspath(os.path.join(os.path.expanduser('~'),'.komrade'))
PATH_KOMRADE_KEYS = os.path.join(PATH_KOMRADE,'.keys')
PATH_KOMRADE_DATA = os.path.join(PATH_KOMRADE,'.data')
for x in [PATH_KOMRADE,PATH_KOMRADE_DATA,PATH_KOMRADE_KEYS]:
    if not os.path.exists(x):
        os.makedirs(x)
PATH_CRYPT_OP_KEYS = os.path.join(PATH_KOMRADE_KEYS,'.op.db.keys.crypt')
PATH_CRYPT_OP_DATA = os.path.join(PATH_KOMRADE_DATA,'.op.db.data.encr')
PATH_CRYPT_CA_KEYS = os.path.join(PATH_KOMRADE_KEYS,'.ca.db.keys.crypt')
PATH_CRYPT_CA_DATA = os.path.join(PATH_KOMRADE_DATA,'.ca.db.data.encr')


# etc
BSEP=b'||||||||||'
BSEP2=b'@@@@@@@@@@'
BSEP3=b'##########'

OPERATOR_PUBKEY = b'VUVDMgAAAC1tkzQ1A0FpH7GMJxSJvKASo6U4FknRKadfN7tyXtjclNVoTD7M'
TELEPHONE_PUBKEY = b'VUVDMgAAAC2NxJDgAsleqZ/UlYioesV5Q7y2p+io+LFXffJRG1JXwftVJHA8'
TELEPHONE_PRIVKEY = b'UkVDMgAAAC2eWzy+AFkPLGvdBis/rY3tfi8/SFaHn4Xaxj8eDSFmLAwUo68P'
OPERATOR_NAME = 'TheOperator'
TELEPHONE_NAME = 'TheTelephone'


# key names

KEYNAMES = [
    'pubkey','privkey','adminkey',
    'pubkey_encr','privkey_encr','adminkey_encr',
    'pubkey_decr','privkey_decr','adminkey_decr',
    'pubkey_encr_encr','privkey_encr_encr','adminkey_encr_encr',
    'pubkey_encr_decr','privkey_encr_decr','adminkey_encr_decr',
    'pubkey_decr_encr','privkey_decr_encr','adminkey_decr_encr',
    'pubkey_decr_decr','privkey_decr_decr','adminkey_decr_decr'
]

OPERATOR_INTERCEPT_MESSAGE = "If you'd like to make a call, please hang up and try again. If you need help, hang up, and then dial your operator."



KEYMAKER_DEFAULT_KEYS_TO_SAVE = ['pubkey_encr', 'privkey_encr', 'adminkey_encr']
# KEYMAKER_DEFAULT_KEYS_TO_RETURN =  ['pubkey_decr_encr', 'privkey_decr_encr', 'adminkey_decr_encr']
KEYMAKER_DEFAULT_KEYS_TO_RETURN =  ['pubkey_decr', 'privkey_decr_encr', 'adminkey_decr_encr']
# KEYMAKER_DEFAULT_KEYS_TO_RETURN += ['pubkey_decr_decr', 'privkey_decr_decr', 'adminkey_decr_decr']
KEYMAKER_DEFAULT_KEYS_TO_RETURN += ['privkey_decr_decr', 'adminkey_decr_decr']
KEYMAKER_DEFAULT_KEYS_TO_GEN =  ['pubkey','privkey','adminkey']
KEYMAKER_DEFAULT_KEYS_TO_GEN += ['pubkey_decr','privkey_decr', 'adminkey_decr']
KEYMAKER_DEFAULT_KEYS_TO_GEN += KEYMAKER_DEFAULT_KEYS_TO_SAVE
KEYMAKER_DEFAULT_KEYS_TO_GEN += KEYMAKER_DEFAULT_KEYS_TO_RETURN
KEYMAKER_DEFAULT_KEYS_TO_GEN = list(set(KEYMAKER_DEFAULT_KEYS_TO_GEN))
KEYMAKER_DEFAULT_KEYS_TO_GEN.sort(key=lambda x: x.count('_'))


KEY_TYPE_ASYMMETRIC_PUBKEY = 'asymmetric_pubkey'
KEY_TYPE_ASYMMETRIC_PRIVKEY = 'asymmetric_privkey'
KEY_TYPE_SYMMETRIC_WITHOUT_PASSPHRASE = 'symmetric_key_without_passphrase'
KEY_TYPE_SYMMETRIC_WITH_PASSPHRASE = 'symmetric_key_with_passphrase'
ENCRYPTED_KEY = 'encrypted_key'


KEYMAKER_DEFAULT_KEY_TYPES = {
    'pubkey':KEY_TYPE_ASYMMETRIC_PUBKEY,
    'privkey':KEY_TYPE_ASYMMETRIC_PRIVKEY,
    'adminkey':KEY_TYPE_SYMMETRIC_WITHOUT_PASSPHRASE,
    
    'pubkey_decr':KEY_TYPE_SYMMETRIC_WITHOUT_PASSPHRASE,
    'privkey_decr':KEY_TYPE_SYMMETRIC_WITHOUT_PASSPHRASE,
    'adminkey_decr':KEY_TYPE_SYMMETRIC_WITHOUT_PASSPHRASE,

    'pubkey_decr_decr':KEY_TYPE_SYMMETRIC_WITHOUT_PASSPHRASE,
    'privkey_decr_decr':KEY_TYPE_SYMMETRIC_WITH_PASSPHRASE,
    'adminkey_decr_decr':KEY_TYPE_SYMMETRIC_WITH_PASSPHRASE,

    'pubkey_encr_decr':KEY_TYPE_SYMMETRIC_WITHOUT_PASSPHRASE,
    'privkey_encr_decr':KEY_TYPE_SYMMETRIC_WITH_PASSPHRASE,
    'adminkey_encr_decr':KEY_TYPE_SYMMETRIC_WITH_PASSPHRASE,


    # encrypted keys
    'pubkey_encr':ENCRYPTED_KEY,
    'privkey_encr':ENCRYPTED_KEY,
    'adminkey_encr':ENCRYPTED_KEY,
    'pubkey_encr_encr':ENCRYPTED_KEY,
    'privkey_encr_encr':ENCRYPTED_KEY,
    'adminkey_encr_encr':ENCRYPTED_KEY,
    'pubkey_decr_encr':ENCRYPTED_KEY,
    'privkey_decr_encr':ENCRYPTED_KEY,
    'adminkey_decr_encr':ENCRYPTED_KEY
}
WHY_MSG = 'Forge the password of memory: '