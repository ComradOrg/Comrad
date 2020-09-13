import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
from komrade.backend.keymaker import *

class Komrade(Caller):

    def __init__(self, name=None, passphrase=DEBUG_DEFAULT_PASSPHRASE):
        super().__init__(name=name,passphrase=passphrase)
        self.passphrase=passphprase if passphrase else None
        if SHOW_STATUS:
            from komrade.cli import CLI
            self.cli = CLI(name=name, persona=self)
    #     self.boot(create=False)

    # def boot(self,create=False):
    #     # Do I already have my keys?
    #     # yes? -- login

    #     keys = self.keychain()
    #     if keys.get('pubkey') and keys.get('privkey'):
    #         self.log('booted!')
    #         return True
        
    #     # If not, forge them -- only once!
    #     if not have_keys and create:
    #         self.get_new_keys()


    def exists_locally_as_contact(self):
        return self.pubkey and not self.privkey

    def exists_locally_as_Komrade(self):
        return self.pubkey and self.privkey

    def exists_on_server(self):
        answer = self.phone.ring_ring({
            '_route':'does_username_exist',
            'name':self.name
        })
        self.log('answer??',answer)
        return answer


    # login?
    # def login(self):
        # if keys.get('pubkey') and keys.get('privkey')

    def register(self, name = None, passphrase = None, is_group=None, show_intro=0,show_body=True):
        ## Defaults
        if name and not self.name: self.name=name
        if not name and self.name: name=self.name
        if not name and not self.name: name=''

        
        ## 1) Have name?
        if SHOW_STATUS and show_intro:
            name = self.cli.status_keymaker_part1(name)
        elif not name:
            name = input('@Keymaker: What is the name for this new account?\n@?: ')

        self.log(f'Hello Komrade @Keymaker, I am Komrade @{name}.\n\nI need your help cutting a pair of encryption keys.')

        ## 2) Make pub public/private keys
        keypair = KomradeAsymmetricKey()
        pubkey,privkey = keypair.pubkey_obj,keypair.privkey_obj
        self.log(f'@Keymaker: I have cut a private and public asymmetric key pair\nusing the Elliptic Curve algorithm from Themis:\n\n(1) {pubkey}\n\n(2) {privkey}')

        ## 3) Have passphrase?
        if SHOW_STATUS and not passphrase:
            passphrase = self.cli.status_keymaker_part2(name,passphrase,pubkey,privkey,hasher,self)
        else:
            if not passphrase: passphrase = DEBUG_DEFAULT_PASSPHRASE
            while not passphrase:
                passphrase=getpass('@Keymaker: Enter a memorable password to encrypt your private key with: \n\n')
                clear_screen()
        self.passphrase=passphrase
        ## 4) Get hashed password
        passhash = hasher(passphrase)
        self.log(f'''@Keymaker: I have replaced your password with a disguised, hashed version\nusing a salted SHA-256 algorithm from python's hashlib:\n\n\t{make_key_discreet_str(passhash)}''')
        ## 5) Encrypt private key
        privkey_decr = KomradeSymmetricKeyWithPassphrase(passphrase)
        privkey_encr = privkey_decr.encrypt(privkey.data)
        privkey_encr_obj = KomradeEncryptedAsymmetricPrivateKey(privkey_encr)
        self.log(f"@Keymaker: Store your private key on your device hardware ONLY\nand only as it was encrypted by your password-generated key:\n\n[Encrypted Private Key]\n({make_key_discreet_str(privkey_encr_obj.data_b64)})")

        ## 6) Test keychain works
        privkey_decr2 = KomradeSymmetricKeyWithPassphrase(passphrase)
        assert privkey_decr2.decrypt(privkey_encr) == privkey.data
        
        self._keychain['pubkey']=pubkey
        self._keychain['privkey_encr']=privkey_encr_obj
        # self._keychain['privkey_decr']=privkey_decr
        # we should be able to reassemble privkey now?
        # self.log('this is my keychain now:')
        assert 'privkey' in self.keychain()

        # self.log('My keychain now looks like:',dict_format(self.keychain()))

        ## 6) More narration?
        if SHOW_STATUS:
            self.cli.status_keymaker_part3(privkey,privkey_decr,privkey_encr,passphrase)

        ## 7) Save data to server
        data = {
            'name':name, 
            'pubkey': pubkey.data,
        }
        self.log('@Keymaker: Store your public key both on your device hardware\nas well as register it with Komrade @Operator on the remote server:\n\n',dict_format(data,tab=2))
        
        # ring operator
        # call from phone since I don't have pubkey on record on Op yet
        # self.log('my keychain:',self._keychain,pubkey,self.op._keychain)

        resp_msg_obj = self.ring_ring(
            {
                'name':name, 
                'pubkey': pubkey.data,
            },
            route='register_new_user'
        )
        self.log('register got back from op:',dict_format(resp_msg_obj,tab=2))



    def ring_ring(self,msg,route=None,**y):
        if type(msg)==dict and not ROUTE_KEYNAME in msg:
            msg[ROUTE_KEYNAME]=route
        return super().ring_ring(msg,caller=self,**y)

    def send_msg_to(self,msg,to_whom):
        msg = self.compose_msg_to(msg,to_whom)
        msg.encrypt()
        
        {'_route':'deliver_to', 'msg':msg}
        
        return self.ring_ring(msg)

    

def test_register():
    import random
    num = random.choice(list(range(0,1000)))
    botname=f'marx{str(num).zfill(3)}'
    marxbot = Komrade(botname)
    # marxbot=Komrade()
    marxbot.register(passphrase='spectre')

if __name__=='__main__':
    test_register()
    # marx = Komrade('marx')
    # elon = Komrade('elon')

    # marx.register()
    # # elon.register()
    # # person.register()
    # # print(person.pubkey)

    # # elon.send_msg_to('youre dumb',marx)
    # #Caller('elon').ring_ring({'_route':'say_hello','msg':'my dumb message to operator'})

    # # print(marx.exists_on_server())