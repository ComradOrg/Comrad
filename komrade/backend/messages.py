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
        if not self.caller or not self.callee:
            self.get_callers()


    def __repr__(self):
        return f"""
    
    <MESSAGE>
        self.msg_d={self.msg_d}
        self.to_name={self.to_name}
        self.to_pubkey={self.to_pubkey}
        self.from_name={self.from_name}
        self.from_pubkey={self.from_pubkey}
        self.msg={self.msg}
        self.embedded_msg={self.embedded_msg}
        self._route={self._route}
        self._caller={self.caller}
        self._callee={self.callee}
        self.messenger={self.messenger}
    </MESSAGE>

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
        if self.caller is not None and self.callee is not None:
            return (self.caller,self.callee) 
        alleged_caller = self.get_caller(self.from_name)
        alleged_callee = self.get_caller(self.to_name)
        if not self.caller_records_match(alleged_caller,alleged_callee):
            raise KomradeException('Records of callers on The Operator and the Caller do not match. Something fishy going on?')
        else:
            self.caller = alleged_caller
            self.callee = alleged_callee
        return (alleged_caller,alleged_caller)

    def caller_records_match(self,alleged_caller,alleged_callee):
        alleged_caller_name = self.from_name
        alleged_caller_pubkey = self.from_pubkey
        alleged_callee_name = self.to_name
        alleged_callee_pubkey = self.to_pubkey

        self.log('caller names:',alleged_caller.name, alleged_caller_name)
        self.log('caller pubs:',alleged_caller.pubkey, alleged_caller_pubkey)
        self.log('callee names:',alleged_callee.name, alleged_callee_name)
        self.log('callee pubs:',alleged_callee.pubkey, alleged_callee_pubkey)

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
        caller,callee = self.get_callers()
        self.log(f'attempting to decrypt msg {self.msg} from {caller} to {caller}')
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


    def encrypt(self,recursive=True):
        """
        Assuming that a recursive message looks like this:
        <MESSAGE>
            self.msg_d={'_from_pub': b'UEC2\x00\x00\x00-\x10\xdcu\xc7\x03:\xb6}\xd2\x88\x93E\x88\x00\xed\xda&\x8f\xd0\x1ae\xe1\xa3\x1b=\xd6\xadBB~M\x86\xda\xd57\x8e\xb5', '_from_name': 'TheTelephone', '_to_pub': b'UEC2\x00\x00\x00-W\xbe\xc4\xa2\x02Sm\xe0\xfc\xde\x1c\xbb\xa2E\x8fy \xc7~+\xff\xd7p\xc6s\xab\xe5\xb29M/\xf24\x92\x91n0', '_to_name': 'TheOperator', '_msg': b' \'\x04&h\x00\x00\x00\x00\x01\x01@\x0c\x00\x00\x00\x10\x00\x00\x004\x00\x00\x00\x90\x1a\x88\x89\x93-\x10\xfb\x14\x10\x08M\xc0\xf2_i\x842\xa8k\xcc\xff"c\x0e"x\\"\xaf\x9c\x91>\x87\x9f|~PP\xb5\x02\x91q\\X\xd2\xbdQu\xcc\xd0A\x0b7zL)\x80\x94[\xe7+I\xf1m\x0f\xb4\x80\xc7;\x8fO7\x99\x90d_\xb2y\xc4'}
            self.to_name=TheOperator
            self.to_pubkey=b'UEC2\x00\x00\x00-W\xbe\xc4\xa2\x02Sm\xe0\xfc\xde\x1c\xbb\xa2E\x8fy \xc7~+\xff\xd7p\xc6s\xab\xe5\xb29M/\xf24\x92\x91n0'
            self.from_name=Caller
            self.from_pubkey=b'UEC2\x00\x00\x00-\x10\xdcu\xc7\x03:\xb6}\xd2\x88\x93E\x88\x00\xed\xda&\x8f\xd0\x1ae\xe1\xa3\x1b=\xd6\xadBB~M\x86\xda\xd57\x8e\xb5'
            self.msg=
                <MESSAGE>
                    self.msg_d={'_from_pub': b'UEC2\x00\x00\x00-\x10\xdcu\xc7\x03:\xb6}\xd2\x88\x93E\x88\x00\xed\xda&\x8f\xd0\x1ae\xe1\xa3\x1b=\xd6\xadBB~M\x86\xda\xd57\x8e\xb5', '_from_name': 'TheTelephone', '_to_pub': b'UEC2\x00\x00\x00-W\xbe\xc4\xa2\x02Sm\xe0\xfc\xde\x1c\xbb\xa2E\x8fy \xc7~+\xff\xd7p\xc6s\xab\xe5\xb29M/\xf24\x92\x91n0', '_to_name': 'TheOperator', '_msg': b' \'\x04&h\x00\x00\x00\x00\x01\x01@\x0c\x00\x00\x00\x10\x00\x00\x004\x00\x00\x00\x90\x1a\x88\x89\x93-\x10\xfb\x14\x10\x08M\xc0\xf2_i\x842\xa8k\xcc\xff"c\x0e"x\\"\xaf\x9c\x91>\x87\x9f|~PP\xb5\x02\x91q\\X\xd2\xbdQu\xcc\xd0A\x0b7zL)\x80\x94[\xe7+I\xf1m\x0f\xb4\x80\xc7;\x8fO7\x99\x90d_\xb2y\xc4'}
                    self.to_name=TheOperator
                    self.to_pubkey=b'UEC2\x00\x00\x00-W\xbe\xc4\xa2\x02Sm\xe0\xfc\xde\x1c\xbb\xa2E\x8fy \xc7~+\xff\xd7p\xc6s\xab\xe5\xb29M/\xf24\x92\x91n0'
                    self.from_name=TheTelephone
                    self.from_pubkey=b'UEC2\x00\x00\x00-\x10\xdcu\xc7\x03:\xb6}\xd2\x88\x93E\x88\x00\xed\xda&\x8f\xd0\x1ae\xe1\xa3\x1b=\xd6\xadBB~M\x86\xda\xd57\x8e\xb5'
                    self.msg=b' \'\x04&h\x00\x00\x00\x00\x01\x01@\x0c\x00\x00\x00\x10\x00\x00\x004\x00\x00\x00\x90\x1a\x88\x89\x93-\x10\xfb\x14\x10\x08M\xc0\xf2_i\x842\xa8k\xcc\xff"c\x0e"x\\"\xaf\x9c\x91>\x87\x9f|~PP\xb5\x02\x91q\\X\xd2\xbdQu\xcc\xd0A\x0b7zL)\x80\x94[\xe7+I\xf1m\x0f\xb4\x80\xc7;\x8fO7\x99\x90d_\xb2y\xc4'
                    self._route=None
                    self.caller=<komrade.backend.the_telephone.TheTelephone object at 0x7f0acfbf7e80>
                    self.callee=<komrade.backend.the_operator.TheOperator object at 0x7f0ac868a3c8>
                    self.messenger=None
                </MESSAGE>
            self._route=None
            self.caller=<komrade.backend.the_telephone.TheTelephone object at 0x7f0acfbf7e80>
            self.callee=<komrade.backend.the_operator.TheOperator object at 0x7f0ac868a3c8>
            self.messenger=None
        </MESSAGE>
        """
        if self.is_encrypted: return
        self.log(f'attempting to encrypt msg {self.msg} from {self.caller} to {self.callee}')
        self.log(f'I now look like v1: {self}')

        if not self.has_embedded_msg:
            msg_to_encrypt = self.msg
        elif recursive:
            # first encrypt that message
            self.msg.encrypt()
            # then encrypt *that* msg's entire msg_d
            msg_to_encrypt = self.msg.msg_d
        
        # in both cases, overwrite msg
        encr_msg = self.encrypt_to_send(
            self.msg,
            self.caller.privkey,
            self.callee.pubkey
        )
        self.log('created an encrypted msg:',encr_msg)
        self.msg_decr = self.msg
        self.msg = encr_msg
        self.msg_d['_msg'] = encr_msg
        self.log(f'I now look like v2: {self}')
        self.is_encrypted = False





    ## creating/encrypting/rolling up messages
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
        # otherwise send msg
        msg_encr = self.encrypt_to_send(msg, self.privkey, another.pubkey)
        msg_d = {
            '_from_pub':self.pubkey,
            '_from_name':self.name,
            '_to_pub':another.pubkey,
            '_to_name':another.name,
            '_msg':msg_encr,
        }
        self.log(f'I am a {type(self)} packaging a message to {another}')
        return msg_d

    
    def unpackage_msg_from(self,msg_encr_b,another):
        return self.decrypt_from_send(
            msg_encr_b,
            from_pubkey=another.pubkey,
            to_privkey=self.privkey
        )

    ## msg properties
    @property
    def has_embedded_msg(self):
        return type(self.msg) == Message

    @property
    def messages(self):
        # move through msgs recursively
        msgs = [self] if not self.has_embedded_msg else [self] + self.embedded_msg.messages
        return msgs

    @property
    def route(self):
        for msg in self.messages:
            if msg._route: return msg._route 




    


def test_msg():
    phone = TheTelephone()
    op = TheOperator()

    pprint(op.pubkey)
    print('?keychains?')
    pprint(phone.pubkey)
    
    msg={'_please':'hello_world'}


    resp_msp_obj = phone.ring_ring(msg)
    print(resp_msp_obj) 


if __name__ == '__main__':
    test_msg()