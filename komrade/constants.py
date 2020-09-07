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
# PATH_CRYPT_CA_KEYS = os.path.join(PATH_KOMRADE_KEYS,'.ca.db.keys.crypt')
# PATH_CRYPT_CA_DATA = os.path.join(PATH_KOMRADE_DATA,'.ca.db.data.encr')
PATH_CRYPT_CA_KEYS = PATH_CRYPT_OP_KEYS
PATH_CRYPT_CA_DATA = PATH_CRYPT_OP_DATA

# etc
BSEP=b'||||||||||'
BSEP2=b'@@@@@@@@@@'
BSEP3=b'##########'

OPERATOR_NAME = 'TheOperator'
TELEPHONE_NAME = 'TheTelephone'
PATH_APP = os.path.abspath(os.path.dirname(__file__))
PATH_BUILTIN_KEYCHAINS_ENCR = os.path.join(PATH_APP,'.builtin.keychains.encr')
PATH_BUILTIN_KEYCHAINS_DECR = os.path.join(PATH_APP,'.builtin.keychains.decr')


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



# KEYMAKER_DEFAULT_KEYS_TO_SAVE = ['pubkey_encr', 'privkey_encr', 'adminkey_encr']
# KEYMAKER_DEFAULT_KEYS_TO_RETURN =  ['pubkey_decr_encr', 'privkey_decr_encr', 'adminkey_decr_encr']


# defaults oriented to Callers
KEYMAKER_DEFAULT_KEYS_TO_SAVE = ['pubkey_encr']

KEYMAKER_DEFAULT_KEYS_TO_RETURN = ['privkey_encr',
                                   'adminkey_encr',
                                   'pubkey_decr',
                                   'privkey_decr_encr', 'privkey_decr_decr'
                                   'adminkey_decr_encr', 'adminkey_decr_decr']

KEYMAKER_DEFAULT_KEYS_TO_GEN =  ['pubkey','privkey','adminkey',
                                 'pubkey_decr','privkey_decr', 'adminkey_decr']
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







OPERATOR_KEYCHAIN = b'eyJwdWJrZXlfZW5jciI6IkFBRUJRQXdBQUFBUUFBQUFMUUFBQUJQN2RSYk5Lak0rSVdPZlh1aDVXQ1wvZmxxcnBGSkJGbUlYWWU1UlVuV3A5ekVRUVRldE44dkNjMlFjWHNiMG1qZnJGRWJIWUVWN3ZoXC81TUdWOUc4SktxbERxTVMzcm81TGc9IiwicHVia2V5IjoiVlVWRE1nQUFBQzJFS1pHSUF2bzZmSnQyY1pLMEVyamtcLzBqMCt5blpLRVFcL1VHejdpUE9PT1J4RzAyUE0ifQ=='

TELEPHONE_KEYCHAIN = b'eyJwcml2a2V5X2VuY3IiOiJBQUVCUUF3QUFBQVFBQUFBTFFBQUFJVHJDWVFyZ3V3OStDZGNQZ1ZkbDFsUnNuYWtkNXRENGtLWVhlS1RvcFMzV3JxR0lCNytvNVc4TnQ0dUkwWXpEeFQ5RHZYbW1ZTmk1RTU4eFB0QlZmVjc0d3BUcFkwbVR3RT0iLCJhZG1pbmtleV9lbmNyIjoiQUFFQlFBd0FBQUFRQUFBQUlBQUFBSGo1d2ZjZ1R3QjZ1bmIrMUlPUTQwRGpyOHZSa2d3TVd3UGdoa3h0cENxdUhrQ1pcLzJvZ3pxcEU0SjN2RHRvMHllME41T3FVWXBSQmRkXC9mdGc9PSIsInB1YmtleV9kZWNyIjoiWmZRN3M2R3RIVjNEZjBtd2hNZ1VNNjFydWxHbDl0Z2U2TmRtcnV3R25LZz0iLCJwcml2a2V5X2RlY3JfZW5jciI6IkFBRUJRUXdBQUFBUUFBQUFJQUFBQUJZQUFBQW1HM2d3SDExME91eTdHOHVVdkdWcGhqK0JzMWFaUlpnWWNSSWtRQTBEQUJBQWtCZFNxR2gxc0x4Zm1nVlNNcldHKzZYMndzYnhpYjVSUkFvU1VJQkpGbHkxY21xR1hZYStjcmJ4VGdxWElUUm0iLCJhZG1pbmtleV9kZWNyX2VuY3IiOiJBQUVCUVF3QUFBQVFBQUFBSUFBQUFCWUFBQUNvaGFBdmZEc3phdFlCTWV5anRUdStobnhrUEVsVEFJS1dVTk43UUEwREFCQUFQd1RqNnZaTUdhS2JWUlFGRXBUVFZDQVZCTUE0WlYyZ3BDM2Y2MERubW9vUkJUK3NcL0FLTjZOcDlnUHhqZjF4NCIsInByaXZrZXlfZGVjcl9kZWNyIjoiYzNsdGJXVjBjbWxqWDJ0bGVWOTNhWFJvWDNCaGMzTndhSEpoYzJVPSIsImFkbWlua2V5X2RlY3JfZGVjciI6ImMzbHRiV1YwY21salgydGxlVjkzYVhSb1gzQmhjM053YUhKaGMyVT0iLCJwcml2a2V5IjoiVWtWRE1nQUFBQzIyK2pVa0FJQlN0eHRMNlBWb21wR095S0Q3SDVBWENjcWZibGxpUFNKdmRiY1l6SmkyIn0='
