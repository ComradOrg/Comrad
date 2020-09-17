# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *


# BEGIN PHONE BOOK (in memory singleton mapping)
PHONEBOOK = {}

# Factory constructor
def Komrade(name=None,pubkey=None,*x,**y):
    if issubclass(type(name),Operator): return name
    if name and not pubkey and type(name)==bytes:
        pubkey=b64enc(name)
        name=None  
    

    from komrade.backend.the_operator import TheOperator
    from komrade.backend.the_telephone import TheTelephone
    from komrade.backend.komrades import KomradeX
    global PHONEBOOK
    # already have?

    if not name and not pubkey: return KomradeX()

    if name in PHONEBOOK: return PHONEBOOK[name]
    pk64 = None if not pubkey else b64enc(pubkey)
    if pk64 in PHONEBOOK: return PHONEBOOK[pk64]

    # print(f'finding Komrade {name} / {pubkey} for the first time!')
    # operator?
    if name==OPERATOR_NAME:
        kommie = TheOperator() #(*x,**y)
    if name==TELEPHONE_NAME:
        kommie = TheTelephone() #(*x,**y)
    else:
        # print('booting new kommie')
        kommie = KomradeX(name,*x,**y)
    
    # print('found!',name,PHONEBOOK[name],PHONEBOOK[name].keychain())
    PHONEBOOK[name] = kommie
    if kommie.pubkey:
        PHONEBOOK[kommie.pubkey.data_b64] = kommie

    return kommie




# from komrade.constants import OPERATOR_ROUTES
class Operator(Keymaker):
    ROUTES = [
        'register_new_user',
        'login',
        'deliver_msg',
        'check_msgs',
        'download_msgs',
        'introduce_komrades',
        'post',
        'fetch_posts'
    ]


    def __eq__(self,other):
        if not self.pubkey or not other.pubkey: return False
        return self.pubkey.data == other.pubkey.data

    def __init__(self,
            name=None,
            pubkey=None,
            keychain = {},
            path_crypt_keys=PATH_CRYPT_CA_KEYS,
            path_crypt_data=PATH_CRYPT_CA_DATA
        ):
        
        global PHONEBOOK
        
        # call Keymaker's intro
        super().__init__(
            name=name,
            keychain=keychain,
            path_crypt_keys=path_crypt_keys,
            path_crypt_data=path_crypt_data
        )

        
        # add to phonebook
        if name: PHONEBOOK[name]=self
        if self.pubkey: PHONEBOOK[self.pubkey.data_b64]=self
        self._inbox_crypt=None
        

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


    def compose_msg_to(self,msg,another,incl_from_name=True,incl_to_name=True):
        if not self.privkey or not self.pubkey:
            raise KomradeException('I appear not yet to have an encryption keypair.',self,self.name,self.pubkey,self.privkey,self.keychain())
        if not another.name or not another.pubkey:
            self.log(f'I {self} failed to compose a message to {another} ?')
            raise KomradeException('I do not know the Komrade I am writing to.')

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
        
        msg_obj = Message(msg_d)
        
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
            # new_data = func(**data)
            new_data = func(msg_obj)
            self.log(f'New data was received back from {self}.{route}() route:\b\b{new_data}')
            msg_obj.msg = msg_obj.msg_d['msg'] = new_data

        # try passing it on?
        if msg_obj.has_embedded_msg:
            new_data = self.route_msg(msg_obj.msg)
            msg_obj.msg = msg_obj.msg_d['msg'] = new_data

        if not new_data or not reencrypt:
            # end of the line?
            return msg_obj

        # time to turn around and encrypt
        # @unsure?``
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
        new_msg_obj=self.route_msg(resp_msg_obj,reencrypt=False)
        new_msg = new_msg_obj.msg

        # print('new_msg_obj',new_msg_obj)
        # print('new_msg',new_msg)
        return new_msg

    def pronto_pronto(self, msg_obj):
        self.log(f'''*ring *ring* 
...

{self}: pronto?
{msg_obj.from_whom}: Ciao ciao. I have a message for you:\n{msg_obj}\n''')

        return self.route_msg(msg_obj,reencrypt=True)


    


    ## inboxes?
    def inbox_crypt(self,
            crypt=None,
            uri=None,
            prefix='/inbox/',
            privkey=None,
            pubkey=None,
            encryptor_func=None,
            decryptor_func=None):

        # already
        # if self._inbox_crypt is None:
        # defaults
        if not crypt: crypt=self.crypt_data
        if not uri: uri=self.uri
        
        if not encryptor_func or not decryptor_func:
            if not privkey: privkey=self.privkey
            if not pubkey: pubkey=self.pubkey

            smsg=SMessage(
                privkey.data,
                pubkey.data
            )
            encryptor_func=smsg.wrap
            decryptor_func=smsg.unwrap

        inbox_crypt = CryptList(
            crypt=self.crypt_data,
            keyname=self.uri,
            prefix=prefix,
            encryptor_func=encryptor_func,
            decryptor_func=decryptor_func
        )
        self.log('-->',inbox_crypt)

        return inbox_crypt