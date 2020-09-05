# addresses
KOMRADE_URL = 'komrade.app'
KOMRADE_ONION = 'u7spnj3dmwumzoa4.onion'
KOMRADE_ONION2 = 'rwg4zcnpwshv4laq.onion' #'128.232.229.63' #'komrade.app'


OPERATOR_API_URL = f'http://{KOMRADE_ONION}/op/'


# paths
import os
PATH_KOMRADE = os.path.abspath(os.path.join(os.path.expanduser('~'),'.komrade'))
PATH_OPERATOR = os.path.join(PATH_KOMRADE,'.operator')
PATH_OPERATOR_PUBKEY = os.path.join(PATH_OPERATOR,'.op.key.pub.encr')
PATH_OPERATOR_PRIVKEY = os.path.join(PATH_OPERATOR,'.op.key.priv.encr')
PATH_CRYPT_KEYS = os.path.join(PATH_OPERATOR,'.op.db.keys.crypt')
PATH_CRYPT_DATA = os.path.join(PATH_OPERATOR,'.op.db.data.encr')

# etc
BSEP=b'||||||||||'
BSEP2=b'@@@@@@@@@@'
BSEP3=b'##########'

OPERATOR_PUBKEY = b'VUVDMgAAAC1tkzQ1A0FpH7GMJxSJvKASo6U4FknRKadfN7tyXtjclNVoTD7M'
TELEPHONE_PUBKEY = b'VUVDMgAAAC2NxJDgAsleqZ/UlYioesV5Q7y2p+io+LFXffJRG1JXwftVJHA8'
TELEPHONE_PRIVKEY = b'UkVDMgAAAC2eWzy+AFkPLGvdBis/rY3tfi8/SFaHn4Xaxj8eDSFmLAwUo68P'

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