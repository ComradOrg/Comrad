# addresses
URL_KOMRADE = '128.232.229.63' #'komrade.app'
OPERATOR_API_URL = f'http://{URL_KOMRADE}:6999/op/'


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

OPERATOR_PUBKEY_b64 = b'VUVDMgAAAC2uQwUQAoxUODIy1nGUKc3gnDe94XxFtsMOJMZ8MN9QMrl3nPiP'
import base64
OPERATOR_PUBKEY = base64.b64decode(OPERATOR_PUBKEY_b64)

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
