import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *


class Person(Caller):

    # def ring_ring(self,msg,to_whom = None):
    #     # if no one intended, call the operator
    #     #return super().ring_ring(with_msg,to_phone=self.op)
    #     if not to_whom: to_whom = self.op

    

        # # create a message, caller 2 caller
        # msg_obj = self.compose_msg_to(msg, to_whom)
        
        # # ring 2: use 'Caller' class to dial and get response
        # resp_msg_obj = super().ring_ring(
        #     msg_obj
        # )
        # self.log('resp_msg_encr_caller2caller',resp_msg_encr_caller2caller)

        # # ring 3: decrypt and send back
        # resp_msg_unencr = self.unpackage_msg_from(
        #     msg_encr_caller2caller,
        #     to_whom
        # )
        # self.log('resp_msg_unencr',resp_msg_encr_caller2caller)

        # return resp_msg_unencr

    # def ring_ring(self,with_msg,to_whom = None):
    #     # if no one intended, call the operator
    #     #return super().ring_ring(with_msg,to_phone=self.op)
    #     if not to_whom: to_whom = self.op

    #     # msg should be unencrypted
    #     msg_unencr = with_msg
    #     self.log('msg_unencr',msg_unencr)

    #     # ring 1: encrypt caller2phone
    #     msg_encr_caller2caller = self.package_msg_to(
    #         msg_unencr,
    #         to_whom
    #     )
    #     self.log('msg_encr_caller2caller!',msg_encr_caller2caller)

    #     # ring 2: use 'Caller' class to dial and get response
    #     resp_msg_encr_caller2caller = super().ring_ring(
    #         msg_encr_caller2caller
    #     )
    #     self.log('resp_msg_encr_caller2caller',resp_msg_encr_caller2caller)

    #     # ring 3: decrypt and send back
    #     resp_msg_unencr = self.unpackage_msg_from(
    #         msg_encr_caller2caller,
    #         to_whom
    #     )
    #     self.log('resp_msg_unencr',resp_msg_encr_caller2caller)

    #     return resp_msg_unencr

    def send_msg_to(self,msg,to_whom):
        msg = {'_please':'deliver_to', 'msg':msg}
        return self.ring_ring(msg,to_whom)

    def ring_ring(self,msg,to_whom):
        return super(Caller,self).ring_ring(
            msg,
            to_whom,
            get_resp_from=super().ring_ring
        )



    def register(self, name = None, passphrase = DEBUG_DEFAULT_PASSPHRASE, is_group=None):
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

        # get message back
        msg_obj = self.phone.ring_ring(msg_to_op)
        phone_res = msg_obj.msg
        
        print('GOT BACK!!!',msg_obj)


        # URI id
        uri_id = phone_res.get('uri_id')
        returned_keys = phone_res.get('_keychain')
        self.log('got URI from Op:',uri_id)
        self.log('got returnd keys from Op:',returned_keys)

        # better have the right keys
        assert set(KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_CLIENT) == set(returned_keys.keys())

        # now save these keys!
        saved_keys = self.save_keychain(name,returned_keys,uri_id=uri_id)
        self.log('saved keys!',saved_keys)

        # save my qr?

        # better have the right keys
        # assert set(KEYMAKER_DEFAULT_KEYS_TO_SAVE) == set(saved_keys.keys())

        # success!
        self.log('yay!!!!')
        return saved_keys



    # def register(self,name=None,passphrase=DEBUG_DEFAULT_PASSPHRASE, is_group=None):
    #     # get needed metadata
    #     if not name: name=self.name
    #     if name is None: 
    #         name = input('\nWhat is the name for this account? ')
    #     if passphrase is None:
    #         passphrase = getpass.getpass('\nEnter a memborable password: ')
    #     # if is_group is None:
    #         # is_group = input('\nIs this a group account? [y/N]').strip().lower() == 'y'

    #     # form request to operator
    #     msg_to_op = {'_please':'forge_new_keys'}

    #     msg_response = self.phone.ring_ring(
    #         msg_to_op,
    #         self.op
    #     )

    #     # call and ask operator to register us
        
    #     # for only this one! we skip straight to phone,
    #     # since I don't have any public keys yet

    #     resp = self.phone.ring_ring(msg_to_op)

    #     return resp


    # def get_new_keys(self, name = None, passphrase = DEBUG_DEFAULT_PASSPHRASE, is_group=None):
    #     # get needed metadata
    #     if not name: name=self.name
    #     if name is None: 
    #         name = input('\nWhat is the name for this account? ')
    #     if passphrase is None:
    #         passphrase = getpass.getpass('\nEnter a memborable password: ')
    #     # if is_group is None:
    #         # is_group = input('\nIs this a group account? [y/N]').strip().lower() == 'y'

        

    #     phone_res = self.phone.ring(msg_to_op)
        
    #     # URI id
    #     uri_id = phone_res.get('uri_id')
    #     returned_keys = phone_res.get('_keychain')
    #     self.log('got URI from Op:',uri_id)
    #     self.log('got returnd keys from Op:',returned_keys)

    #     stop

    #     # better have the right keys
    #     assert set(KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_CLIENT) == set(returned_keys.keys())

    #     # now save these keys!
    #     saved_keys = self.save_keychain(name,returned_keys,uri_id=uri_id)
    #     self.log('saved keys!',saved_keys)

    #     # better have the right keys
    #     # assert set(KEYMAKER_DEFAULT_KEYS_TO_SAVE) == set(saved_keys.keys())

    #     # success!
    #     self.log('yay!!!!')
    #     return saved_keys


if __name__=='__main__':
    marx = Person('marx')
    elon = Person('elon')

    # marx.register()
    # elon.register()
    # person.register()
    # print(person.pubkey)

    elon.send_msg_to('youre dumb',marx)