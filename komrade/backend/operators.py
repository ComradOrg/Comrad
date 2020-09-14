# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
# from komrade.backend.crypt import *
# from komrade.backend.keymaker import *
# from komrade.backend.mazes import *
# from komrade.backend.switchboard import *
from komrade.backend import *
        
def locate_an_operator_somehow(str_or_byte_or_obj):
    if issubclass(type(str_or_byte_or_obj),Operator): return str_or_byte_or_obj
    if type(str_or_byte_or_obj)==str: return locate_an_operator(name=str_or_byte_or_obj)
    if type(str_or_byte_or_obj)==bytes: return locate_an_operator(pubkey=str_or_byte_or_obj)
    raise KomradeException(type(str_or_byte_or_obj),'???')

def comlink(name_or_pubkey):
    return locate_an_operator_somehow(name_or_pubkey)

PHONEBOOK = {}

def locate_an_operator(name=None,pubkey=None):
    global OPERATOR,TELEPHONE,PHONEBOOK
    if name in PHONEBOOK: return PHONEBOOK[name]
    # if pubkey in PHONEBOOK: return PHONEBOOK[pubkey]

    from komrade.backend.the_operator import TheOperator
    from komrade.backend.the_telephone import TheTelephone
    from komrade.backend.callers import Caller

    if not OPERATOR: OPERATOR = TheOperator()
    if not TELEPHONE: TELEPHONE = TheTelephone()

    if pubkey:
        assert type(pubkey)==bytes
        if not isBase64(pubkey): pubkey=b64encode(pubkey)
    
    if name == OPERATOR_NAME:
        return OPERATOR
    if pubkey and pubkey == OPERATOR.pubkey:
        return OPERATOR

    if name==TELEPHONE_NAME:
        return TELEPHONE
    if pubkey and pubkey == TELEPHONE.pubkey:
        return TELEPHONE
    

    print('name????',name)
    from komrade.backend.komrades import Komrade
    PHONEBOOK[name] = caller = Komrade(name=name)
    return caller

from komrade.constants import OPERATOR_ROUTES
class Operator(Keymaker):
    ROUTES = OPERATOR_ROUTES
    
    def __init__(self, name=None, passphrase=DEBUG_DEFAULT_PASSPHRASE, pubkey=None, keychain = {}, path_crypt_keys=PATH_CRYPT_CA_KEYS, path_crypt_data=PATH_CRYPT_CA_DATA):
        # print('booting opertor with ...',name,pubkey,'??')

        if pubkey:
            # print(pubkey,'pubkey !?')
            assert type(pubkey)==bytes
            pubkey = b64dec(pubkey)
            if keychain.get('pubkey'):
                kcpubk=keychain.get('pubkey').data if type(keychain.get('pubkey'))!=bytes else keychain.get('pubkey') 
            else:
                keychain['pubkey']=pubkey #KomradeAsymmetricPublicKey(pubkey)
        
        super().__init__(name=name,passphrase=passphrase, keychain=keychain,
                         path_crypt_keys=path_crypt_keys, path_crypt_data=path_crypt_data)
        
        # self.find_pubkey_and_name(name,pubkey)
        # self.log('booted with operator with:',self.name,self.pubkey,self.find_pubkey(name),'??')
        
    # def boot(self):
    #     ## get both name and pubkey somehow
    #     if not self.pubkey and self.name:
    #         self._keychain['pubkey'] = self.find_pubkey()
    #     elif self.pubkey and not self.name:


    # def boot(self,create=False):
    #      # Do I have my keys?
    #     have_keys = self.exists()
        
    #     # If not, forge them -- only once!``
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


    def compose_msg_to(self,msg,another,incl_from_name=1,incl_to_name=1):
        if not self.privkey or not self.pubkey:
            raise KomradeException('why do I have no pub/privkey pair!?',self,self.name,self.pubkey,self.privkey,self.keychain())
        if not another.name or not another.pubkey:
            self.log(f'I {self} failed to compose a message to {another} ?')
            raise KomradeException('why do I not know whom I\'m writing to?')

        # otherwise create msg
        frompub = self.pubkey.data if hasattr(self.pubkey,'data') else self.pubkey 
        topub = another.pubkey.data if hasattr(another.pubkey,'data') else another.pubkey 

        msg_d = {
            'from':frompub,
            # 'from_name':self.name,
            'to':topub,
            # 'to_name':another.name,
            'msg':msg
        }
        if incl_from_name: msg_d['from_name']=self.name
        if incl_to_name: msg_d['to_name']=another.name
        # self.log(f'I am {self} packaging a message to {another}: {msg_d}')
        from komrade.backend.messages import Message
        
        msg_obj = Message(msg_d,from_whom=self,to_whom=another)
        
        # encrypt!
        # msg_obj.encrypt()

        return msg_obj




    def __repr__(self):
        clsname=(type(self)).__name__
        #name = clsname+' '+
        name = '@'+ (self.name if self.name else '?') # if self.name!=clsname else clsname
        # try:
        #     keystr= 'on device: ' + ('+'.join(self.top_keys) if self.pubkey else '')
        # except TypeError:
        #     keystr=''
        # # if self.pubkey:
        keystr=''
        if False:
            pubk=self.pubkey_b64.decode()
            pubk=pubk[-5:]
            pubk = f' ({pubk})'# if pubk else ''
        else:
            pubk = ''
        return f'{name}' #' ({keystr})'

    


    def route_msg(self,msg_obj,reencrypt=True,new_data=None):
        # decrypt
        # self.log('got msg_obj!',msg_obj)
        if msg_obj.is_encrypted:
            msg_obj.decrypt()
        
        # try route
        if msg_obj.route:
            data,route = msg_obj.data, msg_obj.route
            if not hasattr(self,route) or route not in self.ROUTES:
                raise KomradeException(f'Not a valid route!: {route}')
            
            # route it!
            self.log(f'Routing msg to {self}.{route}():\n\n{dict_format(msg_obj.data,tab=4)}')
            func = getattr(self,route)
            new_data = func(**data)
            self.log(f'New data was received back from {self}.{route}() route:\b\b{dict_format(new_data,tab=4)}')
            msg_obj.msg = msg_obj.msg_d['msg'] = new_data

        # try passing it on?
        if msg_obj.has_embedded_msg:
            new_data = self.route_msg(msg_obj.msg)
            msg_obj.msg = msg_obj.msg_d['msg'] = new_data

        if not new_data or not reencrypt:
            # end of the line?
            return msg_obj

        # time to turn around and encrypt
        # @unsure?
        # from komrade.backend.komrades import Komrade
        # if self != self.phone and type(self)!=Komrade:
        #     # if client, let the request rest
        #     return msg_obj

        # # if remote operator, keep going?
        # self.log('time to flip msg around and return to sender. v1:',msg_obj,dict_format(msg_obj.msg_d))#,new_data,reencrypt,msg_obj.route)
        
        
        # new_msg_obj = msg_obj.to_whom.compose_msg_to(
        #     msg=new_data,
        #     another=msg_obj.from_whom
        # ) #msg_obj.mark_return_to_sender()
        # self.log('returning to sender as:',new_msg_obj)
        new_msg_obj = msg_obj.return_to_sender(new_data)

        # encrypt
        if reencrypt:
            # self.log('reencrypting v1',new_msg_obj)
            new_msg_obj.encrypt()
            # self.log('reencrypting v2',new_msg_obj)


        return new_msg_obj


    def ring_ring(self,msg,to_whom,get_resp_from=None,route=None,caller=None):
        # ring ring
        from komrade.cli.artcode import ART_PHONE_SM1
        import textwrap as tw
        nxt=get_class_that_defined_method(get_resp_from).__name__
        nxtfunc=get_resp_from.__name__
#         if from_whom != self:
#             self.status(f'''ring ring! 
# @{self}: *picks up phone*
# @{from_whom}: I have a message I need you to send for me.
# @{self}: To whom?
# @{from_whom}: To @{to_whom}. But not directly.
# @{self}: Who should it I pass it through?
# @{from_whom}: Pass it to {nxt}. Tell them to use "{nxtfunc}".
# @{self}: Got it... So what's the message?
# @{from_whom}: The message is:
#     {dict_format(msg,tab=4)}
# ''')
        if caller!=self:
            from komrade.cli.artcode import ART_PHONE_SM1
            self.log(f'ring ring! I the {self} have received a message from {caller},\n which I will now encrypt and send along to {to_whom}.\n {ART_PHONE_SM1} ')
        else:
            pass
            self.log(f'I ({self}) will now compose and send an encrypted message to {to_whom}.')

        if route and type(msg)==dict and not ROUTE_KEYNAME in msg:
            msg[ROUTE_KEYNAME] = route

        # get encr msg obj
        
        msg_obj = self.compose_msg_to(
            msg,
            to_whom
        )
        self.log(f'Here is the message I will now encrypt and to send to {to_whom}:\n\n {dict_format(msg_obj.msg,tab = 2)}')
        
        # encrypting
        msg_obj.encrypt()

        # pass through the telephone wire by the get_resp_from function
        if not get_resp_from: get_resp_from=to_whom.ring_ring
        resp_msg_obj = get_resp_from(msg_obj.msg_d,caller=caller)
            #self.log('resp_msg_obj <-',resp_msg_obj)
        if not resp_msg_obj:
            print('!! no response from op !!')
            exit()

        # decrypt
        if resp_msg_obj.is_encrypted:
            resp_msg_obj.decrypt()

        # route back?
        return self.route_msg(resp_msg_obj,reencrypt=False).msg





    def pronto_pronto(self, msg_obj):
        self.log(f'''*ring *ring* 
...

{self}: pronto?
{msg_obj.from_whom}: Ciao ciao. I have a message for you:\n{msg_obj}\n''')

        return self.route_msg(msg_obj,reencrypt=True)

        # route_response = self.route_msg(msg_obj)
        # self.log('route_response',route_response)
        # # set this to be the new msg
        # #msg_obj.msg = msg_obj.msg_d['msg'] = response
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
        