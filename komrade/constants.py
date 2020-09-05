# addresses
KOMRADE_URL = 'komrade.app'
KOMRADE_ONION = 'u7spnj3dmwumzoa4.onion'
KOMRADE_ONION2 = 'rwg4zcnpwshv4laq.onion' #'128.232.229.63' #'komrade.app'


OPERATOR_API_URL = f'http://{KOMRADE_ONION}:6999/op/'


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
OPERATOR_PUBKEY = b'UEC2\x00\x00\x00-\x80\x99^\xef\x03PN\xc93`k\xa0\\A\xf6\\q\x0c\x8b\xa6\x1c\xc7I\xfbC\x96\xb5w\xf9\x83U\xe7\x0b\x8fp)\xaa'
TELEPHONE_PUBKEY = b'UEC2\x00\x00\x00-^_\x9a\xad\x02\x1b8\x1b2\xa0U\xb8\xf1\x9ek\x00\x9fO\xb7\xa3\xf3\x1a\x9c\xe0/\xeb\xe9\xfe\xe9\xb8\x14\x9dE\x83\x07V\xe4'
TELEPHONE_PRIVKEY = b'REC2\x00\x00\x00-?Y\xcb\xed\x00+4\xe5M\x8fC\xdd\xb6\xe3\xe4Z)\x01\xbc\x02\r\xb8X\xa4\\\x7f\xb2\xa8\xaeu\xdd\xa6\x84\xe1E\xde\x08'

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
