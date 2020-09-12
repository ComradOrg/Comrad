import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
from komrade.backend.keymaker import *

class Persona(Caller):

    def __init__(self, name=None, passphrase=DEBUG_DEFAULT_PASSPHRASE):
        super().__init__(name=name,passphrase=passphrase)
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

    def exists_locally_as_persona(self):
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
        else:
            name = input('@Keymaker: What is the name for this new account?\n@?: ')

        ## 2) Make pub public/private keys
        keypair = KomradeAsymmetricKey()
        pubkey,privkey = keypair.pubkey_obj,keypair.privkey_obj
        self.log(f'Keymaker has cut private and public keys:\n\n(1) {pubkey}\n\n(2) {privkey}')

        ## 3) Have passphrase?
        if SHOW_STATUS and not passphrase:
            passphrase = self.cli.status_keymaker_part2(name,passphrase,pubkey,privkey,self.crypt_keys.hash,self)
        else:
            if not passphrase: passphrase=getpass('Enter a memorable password to encrypt your private key with: ')

        ## 4) Get hashed password
        passhash = self.crypt_keys.hash(passphrase.encode())
        self.log(f'''Keymaker has created a symmetric encryption cell using the disguised password:\n\n\t(2A) [Symmetric Encryption Key]\n\t({make_key_discreet_str(passhash)})''')

        ## 5) Encrypt private key
        privkey_decr = KomradeSymmetricKeyWithPassphrase(passhash)
        privkey_encr = privkey_decr.encrypt(privkey.data)
        privkey_encr_obj = KomradeEncryptedAsymmetricPrivateKey(privkey_encr)
        self.log(f"This pass-generated key has now transformed the private key (2) into the following encrypted form (redacted):\n\n\t(2B) [Encrypted Private Key]\n\t({make_key_discreet_str(privkey_encr_obj.data_b64)})")

        ## 6) More narration?
        if SHOW_STATUS:
            self.cli.status_keymaker_part3(privkey,privkey_decr,privkey_encr,passphrase)

        ## 7) Save data to server
        data = {
            'name':name, 
            'pubkey': pubkey.data,
            ROUTE_KEYNAME:'register_new_user'
        }
        self.log('sending to server:',dict_format(data,tab=2))
        # msg_to_op = self.compose_msg_to(data, self.op)
        
        # ring operator
        # call from phone since I don't have pubkey on record on Op yet
        # self.log('my keychain:',self._keychain,pubkey,self.op._keychain)
        self._keychain['pubkey']=pubkey.data
        self._keychain['privkey']=privkey.data

        resp_msg_obj = self.ring_ring(data)
        self.log('register got back from op:',dict_format(resp_msg_obj,tab=2))



    def ring_ring(self,msg):
        return super().ring_ring(msg)

    def send_msg_to(self,msg,to_whom):
        msg = self.compose_msg_to(msg,to_whom)
        msg.encrypt()
        
        {'_route':'deliver_to', 'msg':msg}
        
        return self.ring_ring(msg)

    

def test_register():
    import random
    num = random.choice(list(range(0,1000)))
    botname=f'marx{str(num).zfill(3)}'
    marxbot = Persona(botname)
    # marxbot=Persona()
    marxbot.register(passphrase='communise')

if __name__=='__main__':
    test_register()
    # marx = Persona('marx')
    # elon = Persona('elon')

    # marx.register()
    # # elon.register()
    # # person.register()
    # # print(person.pubkey)

    # # elon.send_msg_to('youre dumb',marx)
    # #Caller('elon').ring_ring({'_route':'say_hello','_msg':'my dumb message to operator'})

    # # print(marx.exists_on_server())