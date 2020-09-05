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
OPERATOR_PUBKEY = b'VUVDMgAAAC0Tfih+A1Rc0gslfhx6+WzC4qyFVZF+QFjGJH3sw/RyG5/mRILW'
TELEPHONE_PUBKEY = b'VUVDMgAAAC0QnMrAA18GOJIg9ouLVvd8Ac/9mZK9GLOb/CMztWGx4GlLP8PP'
TELEPHONE_PRIVKEY = b'UkVDMgAAAC1/aQiQAPWROJRkio2C/qT1ora5ak/ImwLoP1SdTxco+/1Q8qNC'
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