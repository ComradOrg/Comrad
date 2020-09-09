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
    def __init__(self,msg_d,caller=None,callee=None):
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
        self.embedded_msg=None  # only if this message has an embedded one
        self._route=msg_d.get(ROUTE_KEYNAME)
        self.caller=caller
        self.callee=callee
        # get operators straight away?
        if not self.caller or not self.callee:
            self.get_callers()


    ## loading messages
    def get_callers(self,msg_d):
        if self.caller is not None and self.callee is not None:
            return (self.caller,self.callee) 
        alleged_caller = Operator(alleged_caller_name)
        alleged_callee = Operator(alleged_callee_name)
        if not self.caller_records_match(msg_d,alleged_caller,alleged_callee):
            raise KomradeException('Records of callers on The Operator and the Caller do not match. Something fishy going on?')
        else:
            self.caller = alleged_caller
            self.callee = alleged_callee
        return (alleged_caller,alleged_caller)

    def caller_records_match(alleged_caller,alleged_callee):
        alleged_caller_name = self.from_name
        alleged_caller_pubkey = self.from_pubkey
        alleged_callee_name = self.to_name
        alleged_callee_pubkey = msg_d.get('_to_pub')
        if alleged_callee.name != alleged_callee_name:
            return False
        if alleged_caller.name != alleged_caller_name:
            return False
        if alleged_callee.pubkey != alleged_callee_pubkey:
            return False
        if alleged_caller.pubkey != alleged_caller_pubkey:
            return False
        return True

    def is_encrypted(self):
        return type(self.msg) == bytes

    def decrypt(self,recursive=True):
        # get callers
        caller,callee = self.get_callers()
        self.log(f'attempting to decrypt msg {self.msg}' from {caller} to {caller}'')
        # decrypt msg
        decr_msg = caller.unpackage_msg_from(
            self.msg,
            callee
        )
        self.msg_encr = self.msg
        self.msg = decr_msg
        self.msg_d['_msg'] = decr_msg
        
        # now, is the decrypted message itself a message?
        if recursive and is_valid_msg_d(decr_msg):
            # then ... make that, a message object and decrypt it too!
            self.embedded_msg = Message(decr_msg)
            self.embedded_msg.decrypt()
        return decr_msg



    ## msg properties
    def has_embedded_msg(self):
        return self.embedded_msg is not None

    @property
    def messages(self):
        # move through msgs recursively
        msgs = [self] if not self.has_embedded_msg else [self] + self.embedded_msg.messages
        return msgs

    @property
    def route(self):
        for msg in self.messages:
            if msg._route: return msg._route 
