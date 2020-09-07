import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
# from komrade.backend.the_telephone import *

# from komrade.backend.the_telephone import *


class Caller(Operator):
    """
    Variant of an Operator which handles local keys and keymaking.
    """

    @property
    def phone(self):
        global TELEPHONE
        from komrade.backend.the_telephone import TheTelephone
        if not TELEPHONE: TELEPHONE=TheTelephone()
        return TELEPHONE
    @property
    def op(self):
        global OPERATOR
        from komrade.backend.the_operator import TheOperator
        if not OPERATOR: OPERATOR=TheOperator()
        return OPERATOR

    def get_new_keys(self, name = None, passphrase = None, is_group=None):
        if not name: name=self.name
        if name is None: 
            name = input('\nWhat is the name for this account? ')
        if passphrase is None:
            passphrase = getpass.getpass('\nEnter a memborable password: ')
        # if is_group is None:
            # is_group = input('\nIs this a group account? [y/N]').strip().lower() == 'y'

        req_json = {
            '_route':'forge_new_keys',
            'name':name,
            'passphrase':hashish(passphrase.encode())
        }

        req_json['key_types'] = {**KEYMAKER_DEFAULT_KEY_TYPES}
        req_json['keys_to_save']=['pubkey_encr','privkey_encr','adminkey_encr']
        req_json['keys_to_return']=['pubkey_decr',
                                    'privkey_decr_encr', 'privkey_decr_decr',
                                    'adminkey_decr_encr', 'adminkey_decr_decr']

        phone_res = self.phone.req(json_coming_from_phone = req_json, caller=self)
        name = phone_res.get('name')
        returned_keys = phone_res.get('_keychain')
        self.log('got returnd keys from Op:',returned_keys)

        # better have the right keys
        assert set(req_json['keys_to_return']) == set(returned_keys.keys())

        # now save these keys!
        saved_keys = self.save_keychain(name,returned_keys)
        self.log('saved keys!',saved_keys)

        # better have the right keys
        assert set(req_json['keys_to_return']) == set(saved_keys.keys())

        # success!
        self.log('yay!!!!')
        return saved_keys
