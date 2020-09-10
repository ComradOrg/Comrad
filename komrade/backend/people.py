import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *


class Persona(Caller):

    def __init__(self, name=None, passphrase=DEBUG_DEFAULT_PASSPHRASE):
        super().__init__(name=name,passphrase=passphrase)
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
        answer = self.ring_ring({
            '_route':'does_username_exist',
            'name':self.name
        })
        self.log('answer??',answer)
        return answer


    # login?
    # def login(self):
        # if keys.get('pubkey') and keys.get('privkey')

    def register(self, name = None, passphrase = None, is_group=None):
        # defaults
        if name and not self.name: self.name=name
        if not name and self.name: name=self.name
        if not name and not self.name: name=''
        
        # ring ring!
        ticks = ['*ring*','*ring ring*','*ring*']
        self.status(None,ART_OLDPHONE3,3,pause=False,ticks = ticks)

        # hello, op?
        self.status(f'\n\n@{name if name else "?"}: Uh yes hello, Operator? I would like to join Komrade, the socialist network. Could you patch me through?',clear=True,pause=True)
        while not name:
            name=self.status(('name','@TheOperator: Of course, Komrade ...?\n@'),clear=False).get('vals',{}).get('name')
            print()
        self.name=name
        self.status(f"@TheOperator: Of course, Komrade @{name}. A fine name. First, though, let me see if by an awkward accident someone has already taken this name.",clear=False)

        # does username exist
        res = self.exists_on_server()
        self.status('I got this result',res,clear=False)
        stop

        exit()

        self.status([
            '''@TheOperator: I could, it's not safe yet. Your information will be exposed all over the internet. You should forge your encryption keys first.''',
            f'@{name}: Fine, but how do I do that?',
            '@TheOperator: Visit the Keymaker.'
        ])

        # ring ring!
        self.status([None,ART_KEY,2],pause=False)

        # some info
        res = self.status([
            # ART_KEY,
            f'{ART_KEY}@{name}: Dear @Keymaker, I would like to forge a new set of keys.',
            f'''@Keymaker: We will make two. A matching, "asymmetric" pair:''',
            '\t1) A "public key" you can share with anyone.',
            '\t2) A "private key" other no one can ever, ever see.',
            'With both together, you can communicate privately and securely with anyone who also has their own key pair.'
        ])
        while not passphrase:
            passphrase1 = getpass(f'What is a *memorable* pass word or phrase? Do not write it down.\n@{name}: ')
            passphrase2 = getpass(f'Could you repeat that?')
            if passphrase1!=passphrase2:
                self.status('Those passwords didn\'t match. Please try again.',clear=False,pause=False)
            else:
                passphrase=passphrase1

        # if not name or name=='?': self.name = name = res['vals'].get('name')
        res = self.status([
            ('passphrase',f'\nWhat is a memorable pass word or phrase? \n@{name}: ',getpass) if not passphrase else False
            ('passphrase2',f'\Could you repeat that? \n@{name}: ',getpass) if not passphrase else False
        ],clear=False) 
        if not passphrase:
            p1,p2=res.get('passphrase'),res.get('passphrase2')
            # if p1!=p2
            # passphrase = passphrase

        # make and save keys locally
        uri_id,keys_returned = self.forge_new_keys(
            name=name,
            passphrase=passphrase,
            keys_to_save = KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_CLIENT,
            keys_to_return = KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_SERVER
        )
        self.log(f'my new uri is {uri_id} and I got new keys!: {dict_format(keys_returned)}')

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
    # botname=f'marx{str(num).zfill(3)}'
    # marxbot = Persona(botname)
    marxbot=Persona()
    marxbot.register()

if __name__=='__main__':
    marx = Persona('marx')
    elon = Persona('elon')

    marx.register()
    # elon.register()
    # person.register()
    # print(person.pubkey)

    # elon.send_msg_to('youre dumb',marx)
    #Caller('elon').ring_ring({'_route':'say_hello','_msg':'my dumb message to operator'})

    # print(marx.exists_on_server())