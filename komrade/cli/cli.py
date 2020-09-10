import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
import art



class CLI(Logger):
    ROUTES = {
        'help':'see help messages',
        'register':'register new user',
        'login':'log back in'
    }

    def __init__(self):
        self.name=''
        self.cmd=''

    async def run(self,inp,name=''):
        if name: self.name=name
        clear_screen()
        self.boot()
        self.help()

        if inp: self.route(inp)

        while True:
            try:
                inp=input()
            except KeyboardInterrupt:
                exit()
            self.route(inp)
            await asyncio.sleep(0.5)

    def route(self,inp):
        inp=inp.strip()
        if not inp.startswith('/'): return
        cmd=inp.split()[0]
        dat=inp[len(cmd):].strip()
        cmd=cmd[1:]
        if cmd in self.ROUTES and hasattr(self,cmd):
            f=getattr(self,cmd)
            return f(dat)

    def boot(self):
        print(art.text2art(CLI_TITLE,font=CLI_FONT))

    def help(self):
        print()
        for cmd,info in self.ROUTES.items():
            print(f'    /{cmd}: {info}')
        print('\n')

    def intro(self):
        self.status(None,)
    
    ## routes
    def register(self,name=None):
        # defaults
        if name and not self.name: self.name=name
        if not name and self.name: name=self.name
        if not name and not self.name: name=''
        
        # self.status(None,ART_PAYPHONE,3,pause=False) #,ticks = None)

        # hello, op?
        nm=name if name else '?'
        self.status(
            f'\n\n@{nm}: Uh yes hello, Operator? I would like to join Komrade, the socialist network. Could you patch me through?',clear=False)

        while not name:
            name=self.status(('name','@TheTelephone: Of course, Komrade...?\n@')).get('vals').get('name').strip()
            print()
        self.name = name
        self.persona = Persona(name)
        
        self.status(
            f'@TheTelephone: Of course, Komrade @{name}. A fine name.',

            '''@TheTelephone: However, I'm just the local operator who lives on your device; my only job is to communicate with the remote operator securely.''',
            
            '''Komrade @TheOperator lives on the deep web. She's the one you want to speak with.''',

            f'''@{name}: Hm, ok. Well, could you patch me through to the remote operator then?''',
            
            f'''@{TELEPHONE_NAME}: I could, but it's not safe yet. Your information could be exposed. You need to forge your encryption keys first.''',

            f'@{name}: Fine, but how do I do that?',
            
            f'@{TELEPHONE_NAME}: Visit the Keymaker.',
            
            clear=False,pause=True)




        ### KEYMAKER
        self.status(None,ART_KEY,3,pause=False,clear=False)
        # convo
        self.status('',
            f'@{name}: Hello, Komrade @Keymaker? I would like help forging a new set of keys.',

            f'@Keymaker: Of course, Komrade @{name}.',

            '''We will make three keys. First, a matching, "asymmetric" pair.''',

            '\t1) A "public key" you can share with anyone.',
            
            '\t2) A "private key" other no one can ever, ever see.',

            'With both together, you can communicate privately and securely with anyone who also has their own key pair.',

            'We will use the use the iron-clad Elliptic Curve algorthm to generate the keypair, accessed via a high-level cryptography library, Themis (https://github.com/cossacklabs/themis).',

        )
        
        # make and save keys locally
        self.log(f'{KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_CLIENT + KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_SERVER}!!!!!')
        uri_id,keys_returned = self.persona.forge_new_keys(
            name=name,
            passphrase=None,
            keys_to_save = [],
            keys_to_return = KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_CLIENT + KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_SERVER
        )
        self.status('got back',dict_format(keys_returned))
        #self.log(f'my new uri is {uri_id} and I got new keys!: {dict_format(keys_returned)}')

        self.status(
            'Generating public key now: ',5,'\n\t',repr(KomradeAsymmetricPublicKey(keychain['pubkey'])),'\n\n',
            'Generating private key now: ',5,'\n\t',repr(KomradeAsymmetricPrivateKey(keychain['privkey'])),
            clear=False,pause=False,end=' ',speed=2
        )


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

def run_cli():
    cli = CLI()
    asyncio.run(cli.run('/register',name='elon'))

if __name__=='__main__':
    run_cli()
    # asyncio.run(test_async())