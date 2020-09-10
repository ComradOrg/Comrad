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


from komrade.constants import OPERATOR_ROUTES
class Operator(Keymaker):
    ROUTES = OPERATOR_ROUTES
    
    def __init__(self, name, passphrase=DEBUG_DEFAULT_PASSPHRASE, keychain = {}, path_crypt_keys=PATH_CRYPT_CA_KEYS, path_crypt_data=PATH_CRYPT_CA_DATA):
        super().__init__(name=name,passphrase=passphrase, keychain=keychain,
                         path_crypt_keys=path_crypt_keys, path_crypt_data=path_crypt_data)
        # self.boot(create=False)

        # connect phonelines?
        from komrade.backend.phonelines import connect_phonelines
        try:
            self.operator_keychain,self.telephone_keychain,self.world_keychain,self.omega_key = connect_phonelines()
        except KeyError:
            pass

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
        # print('unsealed msg:',msg_d)
        from komrade.backend.messages import Message
        msg_obj = Message(msg_d,from_whom=from_whom,to_whom=to_whom)
        # decrypt msg
        return msg_obj


    def __repr__(self):
        clsname=(type(self)).__name__
        name = clsname+' '+self.name if self.name!=clsname else clsname
        keystr='+'.join(self.top_keys) if self.pubkey else ''
        # if self.pubkey:
        if False:
            pubk=self.pubkey_b64.decode()
            pubk=pubk[-5:]
            pubk = f' ({pubk})'# if pubk else ''
        else:
            pubk = ''
        return f'[{name}]{pubk} ({keystr})'

    def locate_an_operator(self,name):
        if name == OPERATOR_NAME:
            return TheOperator()
        if name == TELEPHONE_NAME:
            return TheTelephone()
        return Caller(name)


    def route_msg(self,msg_obj,reencrypt=True):
        # decrypt
        self.log('got msg_obj!',msg_obj)
        if msg_obj.is_encrypted:
            msg_obj.decrypt()
        
        # try route
        if msg_obj.route:
            data,route = msg_obj.data, msg_obj.route
            if not hasattr(self,route) or route not in self.ROUTES:
                raise KomradeException(f'Not a valid route!: {route}')
            
            # route it!
            func = getattr(self,route)
            new_data = func(**data)
            msg_obj.msg = msg_obj.msg_d['_msg'] = new_data

        # try passing it on?
        if msg_obj.has_embedded_msg:
            new_data = self.route_msg(msg_obj.msg)
            msg_obj.msg = msg_obj.msg_d['_msg'] = new_data

        # time to turn around and encrypt
        msg_obj.mark_return_to_sender()
        self.log('returning to sender as:',msg_obj)

        # encrypt
        if reencrypt:
            msg_obj.encrypt()

        return msg_obj


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
        msg_obj = self.compose_msg_to(
            msg,
            to_whom
        )
        self.log(f'ring ring! here is the message object I made, to send to {to_whom}: {msg_obj}')
        
        # encrypting
        msg_obj.encrypt()

        # pass through the telephone wire by the get_resp_from function
        if not get_resp_from: get_resp_from=to_whom.ring_ring
        resp_msg_obj = get_resp_from(msg_obj.msg_d)
        self.log('resp_msg_obj <-',resp_msg_obj)

        # decrypt
        if resp_msg_obj.is_encrypted:
            resp_msg_obj.decrypt()

        # route back?
        return self.route_msg(resp_msg_obj,reencrypt=False).msg





    def pronto_pronto(self, msg_obj):
        self.log(f'''
        pronto pronto!
        >> {msg_obj}
        ''')

        return self.route_msg(msg_obj,reencrypt=True)

        # route_response = self.route_msg(msg_obj)
        # self.log('route_response',route_response)
        # # set this to be the new msg
        # #msg_obj.msg = msg_obj.msg_d['_msg'] = response
        # #self.log('what msg_obj looks like now:',msg_obj)

        # # send new content back
        # # from komrade.backend.messages import Message
        # # if type(route_response)==Message:
        # #     resp_msg_obj = route_response
        # # else:    
        # resp_msg_obj = msg_obj.to_whom.compose_msg_to(
        #     route_response,
        #     msg_obj.from_whom
        # )
        # self.log('resp_msg_obj',resp_msg_obj)
        
        # # re-encrypt
        # if not resp_msg_obj.is_encrypted:
        #     resp_msg_obj.encrypt()
        #     self.log(f're-encrypted: {resp_msg_obj}')
        
        # # pass msg back the chain
        # return resp_msg_obj
        