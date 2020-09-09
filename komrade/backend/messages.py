import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *


def is_valid_msg_d(msg_d):
    if not type(msg_d)==dict: return False
    to_name=msg_d.get('_to_name')
    to_pub=msg_d.get('_to_pub')
    from_name=msg_d.get('_from_name')
    from_pub=msg_d.get('_from_pub')
    msg=msg_d.get('_msg')
    if to_name and to_pub and from_name and from_pub and msg: return True
    return False


class Message(Logger):
    def __init__(self,msg_d,caller=None,callee=None,messenger=None,embedded_msg=None,is_encrypted=False):
        # check input
        if not is_valid_msg_d(msg_d):
            raise KomradeException('This is not a valid msg_d:',msg_d)
        # set fields
        self.msg_d=msg_d
        self.to_name=msg_d.get('_to_name')
        self.to_pubkey=msg_d.get('_to_pub')
        self.from_name=msg_d.get('_from_name')
        self.from_pubkey=msg_d.get('_from_pub')
        self.msg=msg_d.get('_msg')
        self.embedded_msg=embedded_msg  # only if this message has an embedded one
        self._route=msg_d.get(ROUTE_KEYNAME)
        self._caller=caller
        self._callee=callee
        self.messenger=None
        self.is_encrypted=False
        # get operators straight away?
        if not self._caller or not self._callee:
            self.get_callers()

    @property
    def meta_msg(self):
        md={}
        for i,msg in enumerate(reversed(list(self.messages))):
            self.log(f'msg #{i+1}: {msg}')
            dict_merge(md,msg.msg_d)
        # self.log('returning meta')
        return md

    def __repr__(self):
        msg_d_str=dict_format(self.msg_d,tab=6)
        return f"""
    
    <MSG>
        self.caller={self.caller}
        self.callee={self.callee}
        self.msg_d={msg_d_str}
        self.msg={self.msg}
    </MSG>

        """


    def get_caller(self,name):
        if name == OPERATOR_NAME:
            return TheOperator()
        if name == TELEPHONE_NAME:
            return TheTelephone()
        return Caller(name)

    @property
    def caller(self):
        if not self._caller:
            self._caller,self._callee = self.get_callers()
        return self._caller

    @property
    def callee(self):
        if not self._callee:
            self._caller,self._callee = self.get_callers()
        return self._callee
    
    ## loading messages
    def get_callers(self):
        if self._caller is not None and self._callee is not None:
            return (self._caller,self._callee) 
        alleged_caller = self.get_caller(self.from_name)
        alleged_callee = self.get_caller(self.to_name)
        if not self.caller_records_match(alleged_caller,alleged_callee):
            raise KomradeException('Records of callers on The Operator and the Caller do not match. Something fishy going on?')
        else:
            self._caller = alleged_caller
            self._callee = alleged_callee
        return (self._caller,alleged_caller)

    def caller_records_match(self,alleged_caller,alleged_callee):
        alleged_caller_name = self.from_name
        alleged_caller_pubkey = self.from_pubkey
        alleged_callee_name = self.to_name
        alleged_callee_pubkey = self.to_pubkey

        # self.log('caller names:',alleged_caller.name, alleged_caller_name)
        # self.log('caller pubs:',alleged_caller.pubkey, alleged_caller_pubkey)
        # self.log('callee names:',alleged_callee.name, alleged_callee_name)
        # self.log('callee pubs:',alleged_callee.pubkey, alleged_callee_pubkey)

        if alleged_callee.name != alleged_callee_name:
            return False
        if alleged_caller.name != alleged_caller_name:
            return False
        if alleged_callee.pubkey != alleged_callee_pubkey:
            return False
        if alleged_caller.pubkey != alleged_caller_pubkey:
            return False
        return True

    def decrypt(self,recursive=True):
        # get callers
        self.log(f'attempting to decrypt msg',self.msg) # {self.msg} from {caller} to {callee}')

        # decrypt msg
        decr_msg_b = SMessage(
            self.callee.privkey,
            self.caller.pubkey
        ).unwrap(self.msg)
        
        self.log('Am I decrypted?',decr_msg_b)
        
        decr_msg = pickle.loads(decr_msg_b)
        self.log('unpickled:',decr_msg)

        self.msg_encr = self.msg
        self.msg = decr_msg
        self.msg_d['_msg'] = decr_msg

        self.log('got decr msg back:',decr_msg)
        
        # now, is the decrypted message itself a message?
        if recursive and is_valid_msg_d(decr_msg):
            self.log('this is a valid msg in its own right!',decr_msg)
            # then ... make that, a message object and decrypt it too!
            self.msg = Message(decr_msg)
            self.msg.decrypt()
        
        self.log(f'done decrypting! {self}')
        return decr_msg


    def encrypt(self): # each child message should already be encrypted before coming to its parent message ,recursive=False):
        if self.is_encrypted: return
        # self.log(f'attempting to encrypt msg {self.msg} from {self.caller} to {self.callee}')
        self.log(f'About to encrypt self.msg! I now look like v1: {self}')
        
        # binarize msg
        msg_b = pickle.dumps(self.msg)
        # self.log('msg_b = ',msg_b)

        # encrypt it!
        msg_encr = SMessage(
            self.caller.privkey,
            self.callee.pubkey,
        ).wrap(msg_b)

        self.msg_decr = self.msg
        self.msg = msg_encr
        self.msg_d['_msg'] = msg_encr
        self.log(f'Encrypted! I now look like v2: {self}')
        self.is_encrypted = True



    # def decrypt_from_send(self,msg_encr,from_pubkey,to_privkey):
    #     if not msg_encr or not from_pubkey or not to_privkey:
    #         self.log('not enough info!',msg_encr,from_pubkey,to_privkey)
    #         return {}
    #     try:
    #         # decrypt
    #         msg_b = SMessage(
    #             to_privkey,
    #             from_pubkey,
    #         ).unwrap(msg_encr)
    #         # decode
    #         self.log('msg_b??',msg_b)
    #         msg_json = unpackage_from_transmission(msg_b)
    #         self.log('msg_json??',msg_json)
    #         # return
    #         return msg_json
    #     except ThemisError as e:
    #         self.log('unable to decrypt from send!',e)
    #     return {}



    

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