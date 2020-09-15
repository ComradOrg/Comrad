import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *

def is_valid_msg_d(msg_d):
    if not type(msg_d)==dict: return False
    to_name=msg_d.get('to_name')
    to_pub=msg_d.get('to')
    from_name=msg_d.get('from_name')
    from_pub=msg_d.get('from')
    msg=msg_d.get('msg')
    # if to_name and to_pub and from_name and from_pub and msg: return True
    if to_pub and from_pub and msg: return True
    return False


class Message(Logger):
    def __init__(self,msg_d={},from_whom=None,to_whom=None,msg=None):
        # check input
        self.msg_d=msg_d
        self.to_name=msg_d.get('to_name') if not to_whom else to_whom.name
        self.to_pubkey=msg_d.get('to') if not to_whom else to_whom.uri
        self.from_name=msg_d.get('from_name') if not from_whom else from_whom.name
        self.from_pubkey=msg_d.get('from') if not from_whom else from_whom.uri
        self.msg=msg_d.get('msg') if not msg else msg
        self._route=msg_d.get(ROUTE_KEYNAME)
        self._is_encrypted=None

        # reset msg_d
        self.msg_d = {
            'msg':self.msg,
            'to':self.to_pubkey,
            'to_name':self.to_name,
            'from':self.from_pubkey,
            'from_name':self.from_name
        }

    def __repr__(self):
        # self.log('my type??',type(self.msg),self.msg)
        if type(self.msg)==dict:
            if is_valid_msg_d(self.msg):
                import textwrap
                msg = textwrap.indent(repr(Message(self.msg)),' '*10)
            else:
                msg=dict_format(self.msg,tab=6)
        elif type(self.msg)==bytes:
            msg=b64enc_s(self.msg)
        else:
            msg=self.msg
        return f"""    
    from: @{self.from_name if self.from_name else ''} 
          ({b64enc_s(self.from_pubkey)})
    
    to:   @{self.to_name if self.to_name else ''}
          ({b64enc_s(self.to_pubkey)})

    msg:  {msg}
"""


    @property
    def data(self):
        md={}
        msg_d=self.msg_d
        while msg_d:
            for k,v in msg_d.items(): md[k]=v
            msg_d = msg_d.get('msg',{})
            if type(msg_d)!=dict: msg_d=None
        if 'msg' in md and type(md['msg']) == dict:
            del md['msg']
        del md[ROUTE_KEYNAME]
        return md


    def return_to_sender(self,new_msg=None):
        
        self.log('making return to sender. v1:',self)
        
        new_msg = Message(
            {
                'from':self.msg_d.get('to'),
                'to':self.msg_d.get('from'),
                'from_name':self.msg_d.get('to_name'),
                'to_name':self.msg_d.get('from_name'),
                'msg':new_msg if new_msg else self.msg_d.get('msg')
            }
        )

        self.log('returning:',new_msg)
        return new_msg

    @property
    def from_whom(self):
        # from komrade.backend.komrades import Komrade
        return Komrade(self.from_name, pubkey=self.from_pubkey)

    @property
    def to_whom(self):
        # from komrade.backend.komrades import Komrade
        return Komrade(self.to_name, pubkey=self.to_pubkey)
    

    def decrypt(self,recursive=False):
        # check if needs decryption
        if not self.is_encrypted: return

        # otherwise lets do it
        self.msg_encr = self.msg
        self.log(f'Attempting to decrypt:\n{self}')

        # decrypt msg
        # self.log('attempting to decrypt',self.msg,'from',self.from_pubkey,'to',self.to_pubkey, self.to_whom,dict_format(self.to_whom.keychain()),self.to_whom.assemble(self.to_whom.keychain()))
        if not self.to_whom.privkey:
            self.log(f'{self.to_whom} cannot decrypt this message! {dict_format(self.to_whom.keychain())}!\n\n{self.to_whom.name} {self.to_whom.pubkey} {self.to_name} {self.to_pubkey} {self.to_whom.keychain()}')
            return
        
        self.msg = self.msg_d['msg'] = decr_msg_b = SMessage(
            self.to_whom.privkey.data,
            b64dec(self.from_pubkey)
        ).unwrap(self.msg)

        # unpickle        
        self.msg = self.msg_d['msg'] = decr_msg = pickle.loads(decr_msg_b)
        self.log('Message decrypted:\n',self)

        # now, is the decrypted message itself a message?
        if is_valid_msg_d(decr_msg):
            self.log('Once decrypted, I discovered that I contain an enclosed encrypted message!\n\n',self)
            # then ... make that, a message object and decrypt it too!
            self.msg = Message(decr_msg)

            if recursive and self.msg.is_encrypted:
                self.msg.decrypt()

        # self.log(f'done decrypting! {self}')
        return decr_msg

    @property
    def is_encrypted(self):
        return type(self.msg) == bytes
        # if self.msg._is_encrypted is not None:
            # return self.msg._is_encrypted
        


    def encrypt(self): # each child message should already be encrypted before coming to its parent message ,recursive=False):
        if self._is_encrypted: return
        # self.log(f'attempting to encrypt msg {self.msg} from {self.from_whom} to {self.to_whom}')
        self.log(f'Before encrypting the message from @{self.from_name} to @{self.to_name}, it looks like:\n{self}')
        
        # make sure msg is not meeta
        if self.has_embedded_msg:
            self.msg = self.msg.msg_d
            # self.log('woops, first had to replace Message object with dict',self)

        # binarize msg
        msg_b = pickle.dumps(self.msg)

        # encrypt it!
        # self.log('from whom keychain:',self.from_whom.keychain())
        # self.log('to pubkey:',self.to_pubkey)
        msg_encr = SMessage(
            self.from_whom.privkey.data,
            b64dec(self.to_pubkey)
        ).wrap(msg_b)

        self.msg_decr = self.msg
        self.msg_d['msg'] = self.msg = b64encode(msg_encr)
        self.log(f'After encrypting the message from {self.from_whom} to {self.to_whom}, it looks like:\n{self}')
        self.msg_d['msg'] = self.msg = msg_encr
        self._is_encrypted = True


    @property
    def msg_b(self):
        return pickle.dumps(self.msg_d)
    

    ## msg properties
    @property
    def has_embedded_msg(self):
        return type(self.msg) == Message


    @property
    def messages(self):
        # move through msgs recursively
        def _msgs():
            msg=self
            while True:
                yield msg
                if msg.has_embedded_msg:
                    msg=msg.msg
                break
        return list(_msgs())

    @property
    def route(self):
        if type(self.msg)==dict:
            rte=self.msg.get(ROUTE_KEYNAME)
            if rte:
                return rte
        if self.has_embedded_msg:
            return self.msg.route
        return None

    def delete_route(self):
        if type(self.msg)==dict:
            del self.msg[ROUTE_KEYNAME]
            if ROUTE_KEYNAME in self.msg_d['msg']:
                del self.msg_d['msg'][ROUTE_KEYNAME]
            
        if self.has_embedded_msg:
            self.msg.delete_route()

        


    


def test_msg():
    phone = TheTelephone()
    op = TheOperator()

    pprint(op.pubkey)
    print('?keychains?')
    pprint(phone.pubkey)
    
    msg={'_route':'forge_new_keys'}


    resp_msp_obj = phone.ring_ring(msg)
    print(resp_msp_obj) 


if __name__ == '__main__':
    test_msg()