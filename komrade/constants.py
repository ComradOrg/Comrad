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


KEYMAKER_DEFAULT_KEYS_TO_SAVE = ['pubkey_encr']

KEYMAKER_DEFAULT_KEYS_TO_RETURN = ['privkey_encr', 'adminkey_encr',
                                   'pubkey_decr',
                                   'privkey_decr_encr', 'adminkey_decr_encr',
                                   'privkey_decr_decr', 'adminkey_decr_decr']

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






OPERATOR_KEYCHAIN = b'eyJwdWJrZXlfZW5jciI6IkFBRUJRQXdBQUFBUUFBQUFMUUFBQU9tQkdQUEdLN25peUNFZkQ1b1N3TzdLMHo1YzNOblZ3TDZocTBWYVwvUzJqdzg1cTVtbEU0SHQ1czIxRUVGcmxzUThZNDExZGhJaHBYTkcyTm1uZXhSNGVuWlwvNjNyeElGMVE9IiwicHVia2V5IjoiVlVWRE1nQUFBQzJLZmhsaUFsK3JrZzhyUkN6RG1SR2x5Y3ppUGJoS3RFZmpEOFV0NHNkNE55MWV2TEhaIn0='

TELEPHONE_KEYCHAIN = b'eyJwcml2a2V5X2VuY3IiOiJBQUVCUUF3QUFBQVFBQUFBTFFBQUFBUTBmdEFLMkdhZVo5QzNIc2NFZUpPU2w3b25BeVlZV2FZbW9TMDFCUnFcL3NBTTBkd1NDeGZGenRjNm03NVNYU2hONVM4QVFDOFhIamZ1aTBOWXRNUmpBNzZsMHdvM09jSEk9IiwiYWRtaW5rZXlfZW5jciI6IkFBRUJRQXdBQUFBUUFBQUFJQUFBQUhyY2lQM2FMZWI0dVFBZVdlTEJOcDNOOHdDNmJZWVFlNlpjSllCTDlrUW9jczZUODdnTkljNWxcL0p2bWFNbnFPSjBcL3Zka3dJT3FPT2NKT01BPT0iLCJwdWJrZXlfZGVjciI6ImNZWmZ4aDZ5TVZqUFBZcWxMSWZ2SjBpTTU2TGVMRjFUNFV0T1wvTk5YRlJJPSIsInByaXZrZXlfZGVjcl9lbmNyIjoiQUFFQlFRd0FBQUFRQUFBQUlBQUFBQllBQUFESGZrYUlTYWM1K2lPaUlLVFpucW5velZoQnhOclF4MUU2NnFJSlFBMERBQkFBWGRRbFFFcWk2ZTN5OGUyeFNzVTdmbU1URTQ0bnRXNlRsYmZhK1pibG1GNExiTEZOY1RKT0UzUVpkZDljNkNqSCIsImFkbWlua2V5X2RlY3JfZW5jciI6IkFBRUJRUXdBQUFBUUFBQUFJQUFBQUJZQUFBRDFWZEdramVMMzR4ZllDeHNQYjIxZm9Ebkw2eVFESFBJejJrN2tRQTBEQUJBQVcwMHhDdkozR0Ruemx0VFBxdnVlVWs4bW50cDRiWE95eGcyOW02dDllSEVxNjNBXC9IdWV0MkJxM1hXV2xqU2tPIiwicHJpdmtleV9kZWNyX2RlY3IiOiJjM2x0YldWMGNtbGpYMnRsZVY5M2FYUm9YM0JoYzNOd2FISmhjMlU9IiwiYWRtaW5rZXlfZGVjcl9kZWNyIjoiYzNsdGJXVjBjbWxqWDJ0bGVWOTNhWFJvWDNCaGMzTndhSEpoYzJVPSIsInByaXZrZXkiOiJVa1ZETWdBQUFDMFFhekhXQUExeFJxVWxTbSs5cjk4bFdqek1SamFTTW5QWnl6UjBWV3JXeEZGcGRwU2MifQ=='