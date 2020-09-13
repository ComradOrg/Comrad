"""
There is only one operator!
Running on node prime.
"""
# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *


# print(PATH_OPERATOR_WEB_KEYS_URL)


class TheOperator(Operator):
    """
    The remote operator
    """
    @property
    def phone(self):
        global TELEPHONE
        from komrade.backend.the_telephone import TheTelephone
        if not TELEPHONE: TELEPHONE=TheTelephone()
        return TELEPHONE
    

    def __init__(self, name = OPERATOR_NAME, passphrase=None):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """
        self.passphrase=passphrase
        super().__init__(
            name,
            passphrase,
            path_crypt_keys=PATH_CRYPT_OP_KEYS,
            path_crypt_data=PATH_CRYPT_OP_DATA
        )
        from komrade.backend.phonelines import check_phonelines
        keychain = check_phonelines()[OPERATOR_NAME]
        self._keychain = self.load_keychain_from_bytes(keychain)
        self._keychain = self.keychain()
        # self.log('@Operator booted with keychain:',dict_format(self._keychain),'and passphrase',self.passphrase)

    def ring(self,
        from_caller=None,
        to_caller=None,
        json_phone2phone={}, 
        json_caller2phone={},   # (person) -> operator or operator -> (person)
        json_caller2caller={}):
        
        encr_msg_to_send = super().ring(
            from_phone=self,
            to_phone=self.phone,
            from_caller=from_caller,
            to_caller=to_caller,
            json_phone2phone=json_phone2phone, 
            json_caller2phone=json_caller2phone,   # (person) -> operator
            json_caller2caller=json_caller2caller)

        return self.send(encr_msg_to_send)

    # ends the ring_ring() chain
    def answer_phone(self,data_b):
        # route incoming call from the switchboard
        from komrade.cli.artcode import ART_OLDPHONE4
        self.log(f'''Hello, this is the Operator. I heard you say:\n\n {b64enc_s(data_b)}''')

        # unseal
        msg_obj = self.unseal_msg(
            data_b,
            from_whom=self.phone,
            to_whom = self
        )
        self.log(f'Decoding the binary, I understood: {msg_obj}')
        
        # decrypt?
        msg_obj.decrypt()

        # carry out message instructions
        resp_msg_obj = self.pronto_pronto(msg_obj) #,route=msg_obj.route)
        # self.log('route_result <-',resp_msg_obj)

        # send back down encrypted
        
        msg_sealed = pickle.dumps(resp_msg_obj.msg_d)

        # return back to phone and back down to chain
        return msg_sealed




    def send(self,encr_data_b):
        self.log(type(encr_data_b),encr_data_b,'sending!')
        return encr_data_b

    ### ROUTES
        
    def does_username_exist(self,name,**data):
        pubkey=self.crypt_keys.get(name,prefix='/pubkey/')
        self.log(f'looking for {name}, found {pubkey} as pubkey')
        return bool(pubkey)

    def register_new_user(self,name,pubkey,**data):
        # self.log('setting pubkey under name')
        success,ck,cv_b64 = self.crypt_keys.set(name,pubkey,prefix='/pubkey/')
        if not isBase64(pubkey): pubkey=b64encode(pubkey)
        
        self.log(f'''
got result from crypt:
success = {success}
ck = {ck}
cv = {cv_b64}
''')
        success,ck,cv_b64 = self.crypt_keys.set(pubkey,name,prefix='/name/')
        self.log(f'''
        got result from crypt:
        success = {success}
        ck = {ck}
        cv = {cv_b64}
        ''')
        # check input back from crypt
        # if success and b64decode(cv)!=pubkey: success=False
        # if success and name!=self.crypt_keys.key2hash(name): success=False
        from komrade.utils import b64dec
        res = {
            'success':success,
            'pubkey':b64dec(cv_b64),
            'name':name,
        }
        if not success:
            res['status']=self.status(f"{OPERATOR_INTRO}I'm sorry, but I can't register the name of {name}.")
            return res
        self.log('Operator returning result:',dict_format(res,tab=2))
        
        # give back decryptor

        ## success msg
        #
        cvb64=cv_b64#b64encode(cv).decode()
        qrstr=self.qr_str(cvb64)
        res['status']=self.status(f'''{OPERATOR_INTRO}I have successfully registered Komrade {name}.
        
        If you're interested, here's what I did. I stored the public key you gave me, {cvb64}, under the name of "{name}". However, I never save that name directly, but record it only in a disguised, "hashed" form: {ck}. I scrambled "{name}" by running it through a 1-way hashing function, which will always yield the same result: provided you know which function I'm using, and what the secret "salt" is that I add to all the input, a string of text which I keep protected and encrypted on my local hard drive.
        
        The content of your data will therefore not only be encrypted, but its location in my database is obscured even to me. There's no way for me to reverse-engineer the name of {name} from the record I stored it under, {ck}. Unless you explictly ask me for the public key of {name}, I will have no way of accessing that information.
        
        Your name ({name}) and your public key ({cvb64}) are the first two pieces of information you've given me about yourself. Your public key is your 'address' in Komrade: in order for anyone to write to you, or for them to receive messages from you, they'll need to know your public key (and vise versa). The Komrade app should store your public key on your device as a QR code, under ~/.komrade/.contacts/{name}.png. It will look something like this:{qrstr}You can then send this image to anyone by a secure channel (Signal, IRL, etc), or tell them the code directly ({cvb64}).

        By default, if anyone asks me what your public key is, I won't tell them--though I won't be able to avoid hinting that a user exists under this name should someone try to register under that name and I deny them). Instead, if the person who requested your public key insists, I will send you a message (encrypted end-to-end so only you can read it) that the user who met someone would like to introduce themselves to you; I will then send you their name and public key. It's now your move: up to you whether to save them back your public key.

        If you'd like to change this default behavior, e.g. by instead allowing anyone to request your public key, except for those whom you explcitly block, I have also created a super secret administrative record for you to change various settings on your account. This is protected by a separate encryption key which I have generated for you; and this key which is itself encrypted with the password you entered earlier. Don't worry: I never saw that password you typed, since it was given to me already hashed and disguised. Without that hashed passphrase, no one will be able to unlock the administration key; and without the administration key, they won't be able to find the hashed record I stored your user settings under, since I also salted that hash with your own hashed passphrase. Even if someone found the record I stored them under, they wouldn't be able to decrypt the existing settings; and if they can't do that, I won't let them overwrite the record.''')
       
        self.log('Operator returning result:',dict_format(res,tab=2))




def test_op():
    from komrade.backend.the_telephone import TheTelephone

    from getpass import getpass
    op = TheOperator()
    # op.boot()
    
    keychain_op = op.keychain()

    
    phone = TheTelephone()
    # phone.boot()
    keychain_ph = phone.keychain()
    
    
    from pprint import pprint
    print('REASSEMBLED OPERATOR KEYCHAIN')
    pprint(keychain_op)
    # stop

    print('REASSEMBLED TELEPHONE KEYCHAIN')
    pprint(keychain_ph)
    
    # print(op.pubkey(keychain=keychain))
    # print(op.crypt_keys.get(op.pubkey(), prefix='/privkey_encr/'))
    # print(op.crypt_keys.get(op.name, prefix='/pubkey_encr/'))
    # print(op.pubkey_)


    # stop
    
    # pubkey = op.keychain()['pubkey']
    # pubkey_b64 = b64encode(pubkey)
    # print(pubkey)

if __name__ == '__main__': test_op()