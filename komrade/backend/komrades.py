import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
from komrade.backend.keymaker import *








class KomradeX(Caller):

    def __init__(self, name=None, pubkey=None):
        super().__init__(name=name)
        # self.log(f'booted komrade with {name} and {passphrase} and\n\n{dict_format(self.keychain())}')
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
        # self.log(f'booting {self}!',dict_format(keys))

        if keys.get('pubkey') and keys.get('privkey'):
            # self.log('already booted! @'+self.name)
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


    def exists_locally(self):
        return bool(self.pubkey)

    def exists_locally_as_contact(self):
        return bool(self.pubkey) and not bool(self.privkey)

    def exists_locally_as_account(self):
        return bool(self.pubkey) and bool(self.privkey_encr)

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
        # global PHONEBOOK
        
        # print('got name:',name)
        ## Defaults
        if name and not self.name: self.name=name
        if not name and self.name: name=self.name
        # if not name and not self.name: name=''
        # print('got name',name)

        # already have it?
        if self.exists_locally_as_account():
            return {'success':False, 'status':'You have already created this account.'}
        
        if self.exists_locally_as_contact():
            return {'success':False, 'status':'This is already a contact of yours'}

        
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

        # More narration?
        if SHOW_STATUS: self.cli.status_keymaker_part3(privkey,privkey_decr,privkey_encr,passphrase)

        # 6) Save for now on client -- will delete if fails on server
        
        # storing myself in memory phonebook
        # PHONEBOOK[name]=self

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
        assert pubkey_b == pubkey.data
        uri_id = pubkey.data_b64
        sec_login = resp_msg_d.get('secret_login')
        
        self.log(f'''Now saving name and public key on local device:''')
        self.crypt_keys.set(name, pubkey_b, prefix='/pubkey/')
        self.crypt_keys.set(uri_id, name, prefix='/name/')
        self.crypt_keys.set(uri_id,sec_login,prefix='/secret_login/')

        # store privkey pieces
        self.crypt_keys.set(uri_id, privkey_encr_obj.data, prefix='/privkey_encr/')
        # just to show we used a passphrase -->
        self.crypt_keys.set(uri_id, KomradeSymmetricKeyWithPassphrase.__name__, prefix='/privkey_decr/')


        # save qr too:
        self.save_uri_as_qrcode(uri_id)
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
        # what keys do I have?
        keys = self.keychain()
        # self.log('here are my keys:',dict_format(keys))


        # check hardware
        if not 'pubkey' in keys:
            emsg='''Login impossible. I do not have this komrade's public key, much less private one.'''
            # self.log()
            return {'success':False, 'status':emsg}

        if not 'privkey_encr' in keys:
            emsg='''Login impossible. I do not have this komrade's private key on this hardware.'''
            self.log(emsg)
            return {'success':False, 'status':emsg}
        
        if not 'privkey' in keys:
            emsg='''Login failed. Private key did not unlock from passphrase.'''
            return {'success':False, 'status': emsg}

        # compose message
        msg = {
            'name':self.name,
            'pubkey':keys['pubkey'].data,
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


    def contacts(self):
        # who do I know?
        return sorted([fn.split('.png')[0] for fn in os.listdir(PATH_QRCODES)])




    def ring_ring(self,msg,route=None,**y):
        if type(msg)==dict and not ROUTE_KEYNAME in msg:
            msg[ROUTE_KEYNAME]=route
        return super().ring_ring(msg,caller=self,**y)

    
    
    def msg(self,someone,something):
        # find or boot
        someone = Komrade(someone)
        self.log(f'found {someone}')
        
        # can we?
        if not someone.pubkey:
            self.log(f'''Don't know the public key of {someone}!''')

        msg_obj = self.compose_msg_to(
            something,
            someone
        )
        self.log('composed msg:',msg_obj)
        
        # encrypting
        msg_obj.encrypt()

        # attaching
        direct_msg_data = msg_obj.msg
        self.log('going to send only this to op:',direct_msg_data)

        # enclosing
        msg_to_op = {
            'deliver_from':self.pubkey.data_b64,
            'deliver_to':someone.pubkey.data_b64,
            'deliver_msg':direct_msg_data,
        }

        self.log('going to send msg to op?',msg_to_op)
        
        return self.ring_ring(
            msg_to_op,
            route='deliver_msg'
        )

    def check_msgs(self,inbox=None):
        if not self.pubkey and self.privkey:
            return {'success':False,'status':'Need to be logged in'}
        
        # checking my own mail I presume?
        if not inbox:
            inbox=self.pubkey.data_b64

        # send info op needs
        msg = {
            'secret_login':self.secret_login,
            'name':self.name,
            'pubkey':self.pubkey.data_b64,
            'inbox':inbox
        }
        self.log('sending msg to op:',msg)

        res = self.ring_ring(msg,route='check_msgs')
        self.log('got back response:',res)

        # # decrypt?
        # SMessage(
        #     self.privkey.data,
        #     self.op.pubkey.data
        # ).unwrap()
        return res

    

def test_register():
    import random
    num = random.choice(list(range(0,1000)))
    botname=f'marx{str(num).zfill(3)}'
    marxbot = Komrade(botname)
    # marxbot=Komrade()
    marxbot.register(passphrase='boo')



def test_msg():
    z = comlink('zuck')
    z.login(passphrase='eee')
    
    s = comlink('sergey')
    
    z.send_msg_to('you ssssssuck')


def test_loading():
    z1 = Komrade('elon')
    # z1.register()
    print(z1.keychain())
    # exit()

    z2 = Komrade(b'VUVDMgAAAC08BCMVA+0dMJXc66/W7hty669+3/3S61Q1yjmgJW8I0k3lqfDi')
    print(z2)
    print(z2.keychain())

    pprint(PHONEBOOK)

    return
    
    # z1.login()


if __name__=='__main__':
    test_loading()