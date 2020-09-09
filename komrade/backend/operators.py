# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
# from komrade.backend.crypt import *
# from komrade.backend.keymaker import *
# from komrade.backend.mazes import *
# from komrade.backend.switchboard import *
from komrade.backend import *



class Operator(Keymaker):
    
    def __init__(self, name, passphrase=DEBUG_DEFAULT_PASSPHRASE, keychain = {}, path_crypt_keys=PATH_CRYPT_CA_KEYS, path_crypt_data=PATH_CRYPT_CA_DATA):
        super().__init__(name=name,passphrase=passphrase, keychain=keychain,
                         path_crypt_keys=path_crypt_keys, path_crypt_data=path_crypt_data)
        self.boot(create=False)

        # connect phonelines?
        from komrade.backend.phonelines import connect_phonelines
        self.operator_keychain,self.telephone_keychain,self.omega_key = connect_phonelines()

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


    def compose_msg_to(self,msg,another):
        if not self.privkey or not self.pubkey:
            raise KomradeException('why do I have no pub/privkey pair!?',self,self.name,self.pubkey,self.privkey,self.keychain())
        if not another.name or not another.pubkey:
            raise KomradeException('why do I not know whom I\'m writing to?')

        # otherwise create msg
        msg_d = {
            '_from_pub':self.pubkey,
            '_from_name':self.name,
            '_to_pub':another.pubkey,
            '_to_name':another.name,
            '_msg':msg,
        }
        self.log(f'I am a {type(self)} packaging a message to {another}: {msg_d}')
        
        from komrade.backend.messages import Message
        msg_obj = Message(msg_d,caller=self,callee=another)
        self.log('created msg obj:',msg_obj)

        return msg_obj

    def seal_msg(self,msg_obj):
        # make sure encrypted
        msg_obj.encrypt()
        # return pure binary version of self's entire msg_d
        msg_b = package_for_transmission(msg_obj.msg_d)
        # encrypte by omega key
        msg_b_encr = self.omega_key.encrypt(msg_b)
        return msg_b_encr

    def unseal_msg(self,msg_b_encr):
        # decrypt by omega
        msg_b = self.omega_key.decrypt(msg_b_encr)
        # unpackage from transmission
        msg_d = unpackage_from_transmission(msg_b)
        # get message obj
        print('unsealed msg:',msg_d)
        from komrade.backend.messages import Message
        msg_obj = Message(msg_d)
        # decrypt msg
        msg_obj.decrypt()
        return msg_obj

    # def package_msg_to(self,msg,another):
    #     # otherwise send msg
    #     return self.compose_msg_to(msg,another)

    
    # def unpackage_msg_from(self,msg_encr_b,another):
    #     return self.decrypt_from_send(
    #         msg_encr_b,
    #         from_pubkey=another.pubkey,
    #         to_privkey=self.privkey
    #     )

    
    # self = caller
    # towhom = phone
    # bywayof = op
    def ring_ring(self,msg,to_whom,get_resp_from=None):
        # get encr msg obj
        msg_obj = self.compose_msg_to(msg, to_whom)
        # pass onto next person

        # get pure encrypted binary, sealed
        msg_sealed = self.seal_msg(msg_obj)
        
        # pass onto next person...
        if not get_resp_from: get_resp_from=to_whom.ring_ring
        resp_msg_b = get_resp_from(msg_sealed)

        # unseal msg
        resp_msg_obj = self.unseal_msg(resp_msg_b)

        return resp_msg_obj
        