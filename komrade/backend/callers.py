import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
# from komrade.backend.the_telephone import *

# from komrade.backend.the_telephone import *


class Caller(Operator):
    """
    Variant of an Operator which handles local keys and keymaking.
    """



    def ring_ring(self,with_msg,to_phone=None):
        # message should be encrypted caller2caller (by Person.ring)
        msg_encr_caller2caller = with_msg

        # Caller can only encrypt for Operator (end phone)
        to_whom = to_phone

        # ring 1: encrypt caller2phone
        msg_encr_caller2caller_caller2phone = self.package_msg_to(
            msg_encr_caller2caller,
            to_whom
        )
        self.log('msg_encr_caller2caller_caller2phone',msg_encr_caller2caller_caller2phone)


        # ring 2: dial and get response
        resp_msg_encr_caller2caller_caller2phone = self.phone.ring_ring(
            msg_encr_caller2caller_caller2phone
        )
        self.log('resp_msg_encr_caller2caller_caller2phone',resp_msg_encr_caller2caller_caller2phone)


        # ring 3: decrypt and send back
        resp_msg_encr_caller2caller = self.unpackage_msg_from(
            resp_msg_encr_caller2caller_caller2phone
        )
        self.log('resp_msg_encr_caller2caller',resp_msg_encr_caller2caller)

        return resp_msg_encr_caller2caller


    def get_new_keys(self, name = None, passphrase = DEBUG_DEFAULT_PASSPHRASE, is_group=None):
        # get needed metadata
        if not name: name=self.name
        if name is None: 
            name = input('\nWhat is the name for this account? ')
        if passphrase is None:
            passphrase = getpass.getpass('\nEnter a memborable password: ')
        # if is_group is None:
            # is_group = input('\nIs this a group account? [y/N]').strip().lower() == 'y'

        # form request
        msg_to_op = {
            '_please':'forge_new_keys',
            'name':name,
            'passphrase':hashish(passphrase.encode())
        }

        phone_res = self.phone.ring(msg_to_op)
        
        # URI id
        uri_id = phone_res.get('uri_id')
        returned_keys = phone_res.get('_keychain')
        self.log('got URI from Op:',uri_id)
        self.log('got returnd keys from Op:',returned_keys)

        stop

        # better have the right keys
        assert set(KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_CLIENT) == set(returned_keys.keys())

        # now save these keys!
        saved_keys = self.save_keychain(name,returned_keys,uri_id=uri_id)
        self.log('saved keys!',saved_keys)

        # better have the right keys
        # assert set(KEYMAKER_DEFAULT_KEYS_TO_SAVE) == set(saved_keys.keys())

        # success!
        self.log('yay!!!!')
        return saved_keys
