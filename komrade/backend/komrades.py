import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
from komrade.backend.keymaker import *

class Komrade(Caller):

    def __init__(self, name=None, passphrase=DEBUG_DEFAULT_PASSPHRASE):
        super().__init__(name=name,passphrase=passphrase)
        self.log(f'booted komrade with {name} and {passphrase} and\n\n{dict_format(self.keychain())}')
        # if SHOW_STATUS:
        #     from komrade.cli import CLI
        #     self.cli = CLI(name=name, komrade=self)
        self.boot(create=False)
        # self.name=name
        # pass

    def boot(self,create=False,ping=False):
        # Do I already have my keys?
        # yes? -- login

        keys = self.keychain()
        if keys.get('pubkey') and keys.get('privkey'):
            self.log('already booted! @'+self.name)
            return True
        
        if self.exists_locally_as_account():
            self.log(f'this account (@{self.name}) can be logged into')
            return self.login()
            

        elif self.exists_locally_as_contact():
            self.log(f'this account (@{self.name}) is a contact')
            return #pass #???

        elif ping and self.exists_on_server():
            self.log(f'this account exists on server. introduce?')
            return

        elif create:
            self.log('account is free: register?')
            return self.register()



    def exists_locally_as_contact(self):
        return self.pubkey and not self.privkey

    def exists_locally_as_account(self):
        return self.pubkey and self.privkey_encr

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
        # print('got name:',name)
        ## Defaults
        if name and not self.name: self.name=name
        if not name and self.name: name=self.name
        # if not name and not self.name: name=''
        # print('got name',name)
        
        ## 1) Have name?
        tolog=''
        if SHOW_STATUS and show_intro:
            self.name = name = self.cli.status_keymaker_part1(name)
        elif not name:
            self.name = name = input('\nHello, this is Komrade @')
            print('\nI would like to sign up for the socialist network revolution.',flush=True)
            do_pause()
        else:
            print(f'Hello, this is Komrade @{name}.\n\nI would like to sign up for the socialist network revolution.')
            do_pause()
        
        clear_screen()
        self.log(f'@Keymaker: Excellent. But to communicate with komrades securely,\nyou must first cut your public & private encryption keys. ')
        # do_pause()
        ## 2) Make pub public/private keys
        keypair = KomradeAsymmetricKey()
        pubkey,privkey = keypair.pubkey_obj,keypair.privkey_obj
        self.log(f'@Keymaker: I have cut for you a private and public asymmetric key pair\nusing the Elliptic Curve algorithm from Themis cryptography library:\n\n(1) {pubkey}\n\n(2) {privkey}{ART_KEY_PAIR}',clear=False,pause=True)

        ## 3) Have passphrase?
        if SHOW_STATUS and not passphrase:
            passphrase = self.cli.status_keymaker_part2(name,passphrase,pubkey,privkey,hasher,self)
        else:
            if not passphrase: passphrase = DEBUG_DEFAULT_PASSPHRASE
            while not passphrase:
                passphrase=getpass(f'@Keymaker: Enter a memorable password to encrypt your private key with: \n\n@{self.name}: ')
                clear_screen()
        ## 4) Get hashed password
        passhash = hasher(passphrase)
        self.log(f'''@Keymaker: I have replaced your password with a disguised, hashed version\nusing a salted SHA-256 algorithm from python's hashlib:\n\n\t{make_key_discreet_str(passhash)}''')
        ## 5) Encrypt private key
        privkey_decr = KomradeSymmetricKeyWithPassphrase(passphrase)
        privkey_encr = privkey_decr.encrypt(privkey.data)
        privkey_encr_obj = KomradeEncryptedAsymmetricPrivateKey(privkey_encr)
        self.log(f"@Keymaker: Store your private key on your device hardware ONLY\nas it was encrypted by your password-generated key:\n\n[Encrypted Private Key]\n({make_key_discreet_str(privkey_encr_obj.data_b64)})")

        ## 6) Test keychain works
        #privkey_decr2 = KomradeSymmetricKeyWithPassphrase(passphrase)
        #assert privkey_decr2.decrypt(privkey_encr) == privkey.data
        
        self._keychain['pubkey']=pubkey
        self._keychain['privkey_encr']=privkey_encr_obj
        self._keychain['privkey']=privkey
        # self._keychain['privkey_decr']=privkey_decr
        # we should be able to reassemble privkey now?
        # self.log('this is my keychain now:')
        #assert 'privkey' in self.keychain()

        self.log('My keychain now looks like:',dict_format(self.keychain()))

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

        resp_msg_d = self.ring_ring(
            {
                'name':name, 
                'pubkey': pubkey.data,
            },
            route='register_new_user'
        )
        if not resp_msg_d.get('success'):
            self.log(f'Registration failed. Message from operator was:\n\n{dict_format(resp_msg_d)}')
            return
    
        # otherwise, save things on our end
        self.log(f'Registration successful. Message from operator was:\n\n{dict_format(resp_msg_d)}')

        self.name=resp_msg_d.get('name')
        pubkey_b = resp_msg_d.get('pubkey')
        sec_login = resp_msg_d.get('secret_login')

        pubkey=self._keychain['pubkey']=KomradeAsymmetricPublicKey(pubkey_b)
        uri_id = b64enc(pubkey_b)

        self.crypt_keys.set(
            self.name,
            pubkey_b,
            prefix='/pubkey/')
        self.crypt_keys.set(
            uri_id,
            self.name,
            prefix='/name/')
        self.crypt_keys.set(
            uri_id,
            sec_login,
            prefix='/secret_login/'
        )
        self.crypt_keys.set(
            uri_id,
            privkey_encr_obj.data,
            prefix='/privkey_encr/'
        )
        
        self.log(f'''Now saving name and public key on local device:''')

        # save qr too:
        uri_id = b64enc(pubkey_b)
        qr_str=self.qr_str(uri_id)
        fnfn=self.save_uri_as_qrcode(uri_id)
        # self.log(f'saved public key as QR code to:\n {fnfn}\n\n{qr_str}')

        return resp_msg_d

        
        # done!
        self.log(f'Congratulations. Welcome, Komrade {self}.')

    @property
    def secret_login(self):
        return self.crypt_keys.get(
            self.pubkey.data_b64,
            prefix='/secret_login/'
        )

    def login(self,passphrase=None):
        # check hardware
        if not self.pubkey:
            self.log('''Login impossible. I do not have this komrade's public key, much less private one.''')
            return
        if not self.privkey_encr:
            self.log('''Login impossible. I do not have this komrade's private key on this hardware.''')
            return

        # check password
        while not passphrase:
            from getpass import getpass
            passphrase = getpass('@Keymaker: Enter password for {self} in order to decrypt the encrypted private key:\n\n')
        
        # assemble privkey?
        privkey = self.keychain(passphrase=passphrase).get('privkey')
        if not privkey:
            self.log('''Login impossible. I do not have this komrade's private key on this hardware.''')
            return
        
        # compose message
        msg = {
            'name':self.name,
            'pubkey':self.pubkey.data,
            'secret_login':self.secret_login
        }

        # ask operator and get response
        resp_msg = self.ring_ring(
            msg,
            route='login'
        )

        # get result
        self.log('Got result back from operator:',resp_msg)

        return resp_msg



    ## MEETING PEOPLE

    def find(self,someone):
        if type(someone)==str:
            return Komrade(name=someone)
        if type(someone)==bytes:
            return Komrade(pubkey=someone)
        self.log('what is type of someoen here?',type(someone))
        return someone

    def meet(self,someone):
        # get person obj
        someone = self.find(someone)
        self.log('got someone =',someone,type(someone))







    def ring_ring(self,msg,route=None,**y):
        if type(msg)==dict and not ROUTE_KEYNAME in msg:
            msg[ROUTE_KEYNAME]=route
        return super().ring_ring(msg,caller=self,**y)

    
    
    def send_msg_to(self,msg,to_whom):
        to_whom = self.find(to_whom)
        self.log(f'found {to_whom}')
        msg_obj = self.compose_msg_to(
            msg,
            to_whom
        )
        self.log('composed msg:',msg_obj)
        msg_obj.encrypt()
        self.log('going to send msg_d?',msg_obj.msg_d)
        
        return self.ring_ring(msg_obj.msg_d)

    

def test_register():
    import random
    num = random.choice(list(range(0,1000)))
    botname=f'marx{str(num).zfill(3)}'
    marxbot = Komrade(botname)
    # marxbot=Komrade()
    marxbot.register(passphrase='spectre')



def test_msg():
    z = comlink('zuck')
    z.login(passphrase='eee')
    
    s = comlink('sergey')
    
    z.send_msg_to('you ssssssuck')


if __name__=='__main__':
    test_msg()
    # marx = Komrade('marx')
    # elon = Komrade('elon')

    # marx.register()
    # # elon.register()
    # # person.register()
    # # print(person.pubkey)

    # # elon.send_msg_to('youre dumb',marx)
    # #Caller('elon').ring_ring({'_route':'say_hello','msg':'my dumb message to operator'})

    # # print(marx.exists_on_server())