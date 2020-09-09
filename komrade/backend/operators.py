# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
# from komrade.backend.crypt import *
# from komrade.backend.keymaker import *
# from komrade.backend.mazes import *
# from komrade.backend.switchboard import *
from komrade.backend import *
        

def locate_an_operator(name):
    global OPERATOR,TELEPHONE

    from komrade.backend.the_operator import TheOperator
    from komrade.backend.the_telephone import TheTelephone
    from komrade.backend.callers import Caller

    if name == OPERATOR_NAME:
        return OPERATOR if OPERATOR else TheOperator()
    if name == TELEPHONE_NAME:
        return TELEPHONE if TELEPHONE else TheTelephone()
    return Caller(name)


class Operator(Keymaker):
    ROUTES = ['forge_new_keys','does_username_exist','hello_world']
    
    def __init__(self, name, passphrase=DEBUG_DEFAULT_PASSPHRASE, keychain = {}, path_crypt_keys=PATH_CRYPT_CA_KEYS, path_crypt_data=PATH_CRYPT_CA_DATA):
        super().__init__(name=name,passphrase=passphrase, keychain=keychain,
                         path_crypt_keys=path_crypt_keys, path_crypt_data=path_crypt_data)
        # self.boot(create=False)

        # connect phonelines?
        from komrade.backend.phonelines import connect_phonelines
        self.operator_keychain,self.telephone_keychain,self.omega_key = connect_phonelines()

    # def boot(self,create=False):
    #      # Do I have my keys?
    #     have_keys = self.exists()
        
    #     # If not, forge them -- only once!
    #     if not have_keys and create:
    #         self.get_new_keys()
        
    
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
        # self.log(f'I am {self} packaging a message to {another}: {msg_d}')
        from komrade.backend.messages import Message
        
        msg_obj = Message(msg_d,from_whom=self,to_whom=another)
        
        # encrypt!
        # msg_obj.encrypt()

        return msg_obj

    # def compose_reply(self,msg,another):


    def seal_msg(self,msg_d):
        # make sure encrypted
        self.log('sealing msg!:',dict_format(msg_d))
        # msg_obj.encrypt(recursive=True)
        # return pure binary version of self's entire msg_d
        msg_b = pickle.dumps(msg_d)
        self.log('pickled!',msg_b)

        # encrypt by omega key
        msg_b_encr = self.omega_key.encrypt(msg_b)
        self.log('final seal:',msg_b_encr)

        return msg_b_encr

    def unseal_msg(self,msg_b_encr,from_whom=None,to_whom=None):
        # default to assumption that I am the recipient
        if not to_whom: to_whom=self
        # decrypt by omega
        msg_b = self.omega_key.decrypt(msg_b_encr)
        # unpackage from transmission
        msg_d = pickle.loads(msg_b)
        # get message obj
        print('unsealed msg:',msg_d)
        from komrade.backend.messages import Message
        msg_obj = Message(msg_d,from_whom=from_whom,to_whom=to_whom)
        # decrypt msg
        msg_obj.decrypt()
        return msg_obj


    def __repr__(self):
        clsname=(type(self)).__name__
        keystr='+'.join(self.top_keys)
        return f'[{clsname}] {self.name} ({keystr})'

    def locate_an_operator(self,name):
        if name == OPERATOR_NAME:
            return TheOperator()
        if name == TELEPHONE_NAME:
            return TheTelephone()
        return Caller(name)


    def ring_ring(self,msg,to_whom,get_resp_from=None):
        # ring ring
        self.log(f'''
        ring ring!
        I am {self}.
        I have been told to pass onto {to_whom},
        by way of function {get_resp_from},
        the following msg:
        {dict_format(msg,tab=5)}
        ''')
        
        # get encr msg obj
        msg_obj = self.compose_msg_to(msg, to_whom)
        self.log(f'ring ring! here is the message object I made, to send to {to_whom}: {msg_obj}')
        
        # encrypting
        msg_obj.encrypt()
        # get pure encrypted binary, sealed
        #msg_sealed = self.seal_msg(msg_obj)
        
        # pass onto next person...
        if not get_resp_from: get_resp_from=to_whom.ring_ring
        resp_msg_obj = get_resp_from(msg_obj.msg_d)
        self.log('resp_msg_obj <-',resp_msg_obj)

        # decrypt?
        resp_msg_obj.decrypt()

        # unseal msg
        # resp_msg_obj = self.unseal_msg(resp_msg_b)

        return resp_msg_obj

    def route(self,data,route):
        if hasattr(self,route) and route in self.ROUTES:
            func = getattr(self,route)
            return func(**data)
        
    
    def pronto_pronto(self, msg_obj):
        self.log(f'''
        >> {msg_obj}
        ''')

        # decrypt
        if msg_obj.is_encrypted:
            msg_obj.decrypt()
        # are there instructions for us?
        if msg_obj.route:
            # get result from routing
            self.log(f'routing msg to self.{msg_obj.route}(**{msg_obj.data})')
            response = self.route(msg_obj.data, route=msg_obj.route)
            self.log('route response:',response)
        # can we pass the buck on?
        elif msg_obj.has_embedded_msg:
            embedded_msg = msg_obj.msg
            embedded_recipient = embedded_msg.to_whom
            # whew, then we can make someone else take the phone
            self.log(f'passing msg onto {embedded_recipient} ...')
            
            response = embedded_recipient.pronto_pronto(embedded_msg) 
            self.log(f'passed msg onto {embedded_recipient}, got this response: {response} ...')
        # otherwise what are we doing?
        else: 
            raise KomradeException('No route, no embedded msg. What to do?')
        
        # set this to be the new msg
        #msg_obj.msg = msg_obj.msg_d['_msg'] = response
        #self.log('what msg_obj looks like now:',msg_obj)

        # send new content back
        resp_msg_obj = msg_obj.to_whom.compose_msg_to(
            response,
            msg_obj.from_whom
        )
        self.log('resp_msg_obj',resp_msg_obj)
        
        # re-encrypt
        resp_msg_obj.encrypt()
        self.log(f're-encrypted: {resp_msg_obj}')
        
        # pass msg back the chain
        return resp_msg_obj
        