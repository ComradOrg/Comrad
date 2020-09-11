import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
from komrade.backend.keymaker import *

class Persona(Caller):

    def __init__(self, name=None, passphrase=DEBUG_DEFAULT_PASSPHRASE):
        super().__init__(name=name,passphrase=passphrase)
        if SHOW_STATUS:
            from komrade.cli import CLI
            self.cli = CLI()
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
        # defaults
        if name and not self.name: self.name=name
        if not name and self.name: name=self.name
        if not name and not self.name: name=''
        clear_screen()

        # intro narration?
        if SHOW_STATUS and show_intro:
           name = self.cli.status_keymaker_intro(name)



        # 1) forge public/private keys
        keypair = KomradeAsymmetricKey()
        pubkey,privkey = keypair.pubkey_obj,keypair.privkey_obj

        # 2) make sure we have passphrase
        passphrase=self.crypt_keys.hash(b'boogywoogy')
        if SHOW_STATUS and not passphrase:
            passphrase = self.cli.status_keymaker_body(
                name,
                passphrase,
                pubkey,
                privkey,
                self.crypt_keys.hash,
                self
            )
        else:
            if not passphrase: passphrase=getpass('Enter a memorable password to encrypt your private key with: ')

        # 3) form an encryption key
        privkey_decr = KomradeSymmetricKeyWithPassphrase(passphrase)
        privkey_encr = privkey_decr.encrypt(privkey.data)

        self.cli.status_keymaker_part3(privkey,privkey_decr,privkey_encr,passphrase)

        exit()

        # save the ones we should on server
        data = {
            **{'name':name, 'passphrase':self.crypt_keys.hash(passphrase.encode()), ROUTE_KEYNAME:'register_new_user'}, 
            **keys_returned
        }
        self.log('sending to server:',dict_format(data,tab=2))
        # msg_to_op = self.compose_msg_to(data, self.op)
        
        # ring operator
        # call from phone since I don't have pubkey on record on Op yet
        resp_msg_obj = self.phone.ring_ring(data)
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
    marxbot.register()

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