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
        self.log('from privkey =',from_privkey)
        self.log('to pubkey =',to_pubkey)

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
        self.log('KEYCHAINNN ',self.keychain())
        self.log('my privkey',self.privkey)
        self.log('my pubkey',self.pubkey,self.keychain().get('pubkey','!!!?!!?!?!?!?'))
        if not self.privkey or not self.pubkey:
            self.log('why do I have no pub/privkey pair!?',self.privkey,self,self.name)
            return b''
        if not another.name or not another.pubkey:
            self.log('why do I not know whom I\'m writing to?')
            return b''

        # otherwise send msg
        msg = {
            '_from_pub':self.pubkey,
            '_from_name':self.name,
            '_to_pub':another.pubkey,
            '_to_name':another.name,
            '_msg':msg,
        }
        self.log(f'I am a {type(self)} packaging a message to {another}')
        return self.encrypt_to_send(msg, self.privkey, another.pubkey)

    
    def unpackage_msg_from(self,msg_encr_b,another):
        return self.decrypt_from_send(
            msg_encr_b,
            from_pubkey=another.pubkey,
            to_privkey=self.privkey
        )

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

    def is_valid_msg_d(self,msg_d):
        if not type(msg_d)==dict: return False
        to_name=msg_d.get('_to_name')
        to_pub=msg_d.get('_to_pub')
        from_name=msg_d.get('_from_name')
        from_pub=msg_d.get('_from_pub')
        msg=msg_d.get('_msg')
        if to_name and to_pub and from_name and from_pub and msg: return True
        return False
        

    def can_decrypt_this(self,msg_d):
        # check info present
        if not self.is_valid_msg_d(msg_d): return False
        to_name=msg_d.get('_to_name')
        to_pub=msg_d.get('_to_pub')
        if to_name != self.name or to_pub != self.pubkey: return False
        return True

    def unpackage_msg_dict(self,msg_d):
        if self.can_I_decrypt_this(msg_d):
            # get right caller
            alleged_caller_name = _msg.get('_from_name')
            alleged_caller_pub = _msg.get('_from_pub')
            my_record_of_them = Caller(alleged_caller_name)

            if alleged_caller_name == my_record_of_them.name:
                if alleged_caller_pub == my_record_of_them.pubkey:
                    encr_msg=msg_d.get('_msg')

                    try:
                        msg_d['_msg'] = decr_msg = self.unpackage_msg_from(
                            encr_msg,
                            my_record_of_them
                        )
                    except KomradeException as e:
                        self.log('!! e')
        return msg_d

    def msg_is_encrypted(self,_msg_d):
        if not self.is_valid_msg_d(_msg_d): return False
        


    def unroll_decryption_onion(self,msg_d):
        # does message even need decryption?

        # get right caller
        alleged_caller_name = _msg.get('_from_name')
        alleged_caller_pub = _msg.get('_from_pub')
        alleged_callee_name = _msg.get('_to_name')
        alleged_callee_pub = _msg.get('_to_pub')

        alleged_caller = Operator(alleged_caller_name)
        alleged_callee = Operator(alleged_callee_name)

        if alleged_callee.can_decrypt_this()

        if self.can_I_decrypt_this(msg_d,I=):
            msg_d['_msg'] = self.unroll_decryption_onion(msg_d['_msg'])
        return msg_d