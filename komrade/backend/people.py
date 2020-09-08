import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *


class Person(Caller):

    def call_person(self,person):
        pass


    def ring_ring(self,msg_unencr,whom_to_call):
        # ring 1: encrypt caller2phone
        msg_encr_caller2caller = self.package_msg_to(
            msg_unencr,
            whom_to_call
        )
        self.log('msg_encr_caller2caller',msg_encr_caller2caller)

        # ring 2: use 'Caller' class to dial and get response
        resp_msg_encr_caller2caller = super().ring_ring(
            msg_encr_caller2caller
        )
        self.log('resp_msg_encr_caller2caller',resp_msg_encr_caller2caller)

        # ring 3: decrypt and send back
        resp_msg_unencr = self.unpackage_msg_from(
            msg_encr_caller2caller,
            whom_to_call
        )
        self.log('resp_msg_unencr',resp_msg_encr_caller2caller)

        return resp_msg_unencr


    def register(self):
        # get needed metadata
        if not name: name=self.name
        if name is None: 
            name = input('\nWhat is the name for this account? ')
        if passphrase is None:
            passphrase = getpass.getpass('\nEnter a memborable password: ')
        # if is_group is None:
            # is_group = input('\nIs this a group account? [y/N]').strip().lower() == 'y'

        # form request to operator
        msg_to_op = {'_please':'forge_new_keys'}

        # call and ask operator to register us
        resp = self.ring_ring(
            whom=self.op,
            msg_unencr=msg_to_op
        )


    def get_new_keys(self, name = None, passphrase = DEBUG_DEFAULT_PASSPHRASE, is_group=None):
        # get needed metadata
        if not name: name=self.name
        if name is None: 
            name = input('\nWhat is the name for this account? ')
        if passphrase is None:
            passphrase = getpass.getpass('\nEnter a memborable password: ')
        # if is_group is None:
            # is_group = input('\nIs this a group account? [y/N]').strip().lower() == 'y'

        

        phone_res = self.phone.ring_ring(msg_to_op)
        
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
