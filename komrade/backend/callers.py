import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
# from komrade.backend.the_telephone import *

# from komrade.backend.the_telephone import *


class Caller(Operator):
    """
    Variant of an Operator which handles local keys and keymaking.
    """


    def get_new_keys(self, name = None, passphrase = DEBUG_DEFAULT_PASSPHRASE, is_group=None):
        if not name: name=self.name
        if name is None: 
            name = input('\nWhat is the name for this account? ')
        if passphrase is None:
            passphrase = getpass.getpass('\nEnter a memborable password: ')
        # if is_group is None:
            # is_group = input('\nIs this a group account? [y/N]').strip().lower() == 'y'

        # form request
        req_json = {
            '_route':'forge_new_keys',
            'name':name,
            'passphrase':hashish(passphrase.encode())
        }

        # ask operator
        phone_res = self.phone.ring_ring(json_phone2phone=req_json)
        
        # URI id
        uri_id = phone_res.get('uri_id')
        returned_keys = phone_res.get('_keychain')
        self.log('got URI from Op:',uri_id)
        self.log('got returnd keys from Op:',returned_keys)

        stop

        # better have the right keys
        assert set(KEYMAKER_DEFAULT_KEYS_TO_RETURN) == set(returned_keys.keys())

        # now save these keys!
        saved_keys = self.save_keychain(name,returned_keys,uri_id=uri_id)
        self.log('saved keys!',saved_keys)

        # better have the right keys
        # assert set(KEYMAKER_DEFAULT_KEYS_TO_SAVE) == set(saved_keys.keys())

        # success!
        self.log('yay!!!!')
        return saved_keys
