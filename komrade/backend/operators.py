# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *
from komrade.backend.keymaker import *
from komrade.backend.mazes import *
from komrade.backend.switchboard import *




class Operator(Keymaker):
    
    def __init__(self, name, passphrase=DEBUG_DEFAULT_PASSPHRASE, keychain = {}, path_crypt_keys=PATH_CRYPT_CA_KEYS, path_crypt_data=PATH_CRYPT_CA_DATA):
        super().__init__(name=name,passphrase=passphrase, keychain=keychain,
                         path_crypt_keys=path_crypt_keys, path_crypt_data=path_crypt_data)
        self.boot(create=False)

    def boot(self,create=False):
         # Do I have my keys?
        have_keys = self.exists()
        
        # If not, forge them -- only once!
        if not have_keys and create:
            self.get_new_keys()
        
    
    @property
    def phone(self):
        from komrade.backend.the_telephone import TheTelephone
        if type(self)==TheTelephone: return self

        if hasattr(self,'_phone'): return self._phone

        global TELEPHONE,TELEPHONE_KEYCHAIN
        if TELEPHONE: return TELEPHONE

        self._phone=TELEPHONE=TheTelephone()

        return TELEPHONE

    @property
    def op(self):
        from komrade.backend.the_operator import TheOperator
        if type(self)==TheOperator: return self

        if hasattr(self,'_op'): return self._op

        global OPERATOR,OPERATOR_KEYCHAIN
        if OPERATOR: return OPERATOR
        
        self._op=OPERATOR=TheOperator()
        
        return OPERATOR

    def encrypt_to_send(self,msg_json,from_privkey,to_pubkey):
        self.log('msg_json',msg_json)
        self.log('from_privkey',from_privkey)
        self.log('to_pubkey',to_pubkey)
        if not msg_json or not from_privkey or not to_pubkey:
            self.log('not enough info!',msg_json,from_privkey,to_pubkey)
            whattttttt
            return b''
        self.log('packing for transmission: msg_json',type(msg_json),msg_json)
        msg_b = package_for_transmission(msg_json)
        self.log('packing for transmission: msg_b',type(msg_b),msg_b)
        # try:
        msg_encr = SMessage(
            from_privkey,
            to_pubkey,
        ).wrap(msg_b)
        self.log('msg_encr',msg_encr)
        # stop
        return msg_encr
        # except ThemisError as e:
            # self.log('unable to encrypt to send!',e)
        # return b''


    def decrypt_from_send(self,msg_encr,from_pubkey,to_privkey):
        if not msg_encr or not from_pubkey or not to_privkey:
            self.log('not enough info!',msg_encr,from_pubkey,to_privkey)
            return {}
        try:
            # decrypt
            msg_b = SMessage(
                to_privkey,
                from_pubkey,
            ).unwrap(msg_encr)
            # decode
            self.log('msg_b??',msg_b)
            msg_json = unpackage_from_transmission(msg_b)
            self.log('msg_json??',msg_json)
            # return
            return msg_json
        except ThemisError as e:
            self.log('unable to decrypt from send!',e)
        return {}



    def package_msg_to(self,msg,another):
        msg = {
            '_from_pub':self.pubkey,
            '_from_name':self.name,
            '_to_pub':another.pubkey,
            '_to_name':another.name
            '_msg':msg,
        }
        return self.encrypt_to_send(msg, self.privkey, another.pubkey)

    
    def unpackage_msg_from(self,msg_encr_b,another):
        return self.decrypt_from_send(msg_encr_b,another)
        

    # def ring(self,with_msg,to_whom=None,by_way_of=None):
    #     # ring 1: encrypt from me to 'whom'
    #     msg_encr = self.package_msg_to(
    #         with_msg,
    #         whom
    #     )
    #     self.log(f'msg_encr --> {whom} layer 1',msg_encr)

    #     # ring 2: keep ringing via mediator
    #     resp_msg_encr = by_way_of.ring(
    #         msg_encr
    #     )
    #     self.log('resp_msg_encr',resp_msg_encr)

    #     # ring 3: decrypt and send back
    #     resp_msg = self.unpackage_msg_from(
    #         resp_msg_encr,
    #         whom
    #     )
    #     self.log('resp_msg',resp_msg)

    #     return resp_msg