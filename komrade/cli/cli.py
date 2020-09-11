import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
import art
import textwrap as tw



class CLI(Logger):
    ROUTES = {
        'help':'see help messages',
        'register':'register new user',
        'login':'log back in'
    }

    def __init__(self):
        self.name=''
        self.cmd=''

    def run(self,inp='',name=''):
        self.name=name
        clear_screen()
        self.boot()
        self.help()

        if inp: self.route(inp)

        while True:
            try:
                inp=input(f'@{self.name if self.name else "?"}: ')
            except KeyboardInterrupt:
                exit()
            self.route(inp)
            #await asyncio.sleep(0.5)

    def route(self,inp):
        inp=inp.strip()
        if not inp.startswith('/'): return
        cmd=inp.split()[0]
        dat=inp[len(cmd):].strip()
        cmd=cmd[1:]
        if cmd in self.ROUTES and hasattr(self,cmd):
            f=getattr(self,cmd)
            return f(dat)

    def boot(self,indent=5):
        logo=art.text2art(CLI_TITLE,font=CLI_FONT)
        # logo=make_key_discreet_str(logo,chance_bowdlerize=0.1) #.decode()
        logo=tw.indent(logo, ' '*indent)
        scan_print(logo,max_pause=0.005)

    def help(self):
        print()
        for cmd,info in self.ROUTES.items():
            print(f'    /{cmd}: {info}')
            # print('\n')
        print('\n')

    def intro(self):
        self.status(None,)
    
    def register(self,dat):
        self.persona = Persona(self.name)
        self.persona.register()




    ### DIALOGUES

    # hello, op?
    def status_keymaker_intro(self,name):
        self.status(None,{ART_OLDPHONE4+'\n',True},3) #,scan=False,width=None,pause=None,clear=None)
        
        nm=name if name else '?'
        self.status(
            f'\n\n\n@{nm}: Uh yes hello, Operator? I would like to join Komrade, the socialist network. Could you patch me through?',clear=False)

        while not name:
            name=self.status(('name','@TheTelephone: Of course, Komrade...?\n@')).get('vals').get('name').strip()
            print()
        
        self.status(
            f'@TheTelephone: Of course, Komrade @{name}. A fine name.',

            '''@TheTelephone: However, I'm just the local operator who lives on your device; my only job is to communicate with the remote operator securely.''',
            
            '''Komrade @TheOperator lives on the deep web. She's the one you want to speak with.''',

            None,{ART_OLDPHONE4},f'''@{name}: Hm, ok. Well, could you patch me through to the remote operator then?''',
            
            f'''@{TELEPHONE_NAME}: I could, but it's not safe yet. Your information could be exposed. You need to forge your encryption keys first.''',

            f'@{name}: Fine, but how do I do that?',
            
            f'@{TELEPHONE_NAME}: Visit the Keymaker.',
            
            clear=False,pause=True)

        ### KEYMAKER
        self.status(None,{tw.indent(ART_KEY,' '*5)+'\n',True},3) #,clear=False,indent=10,pause=False)
        # convo
        self.status(
            f'\n@{name}: Hello, Komrade @Keymaker? I would like help forging a new set of keys.',

            f'@Keymaker: Of course, Komrade @{name}.',
        )

        return name



    def status_keymaker_body(self,name,passphrase,pubkey,privkey,hasher):
        # gen what we need
        uri_id = pubkey.data_b64
        qr_str = get_qr_str(uri_id)
        qr_path = os.path.join(PATH_QRCODES,name+'.png')

        # # what are pub/priv?
        # self.status(
        #     'I will forge for you two matching keys, part of an "asymmetric" pair.',
        #     'Please, watch me work.',
            
        #     None,{tw.indent(ART_KEY,' '*5)+'\n'},
            
        #     'I use a high-level cryptographic function from Themis, a well-respected open-source cryptography library.',
        #     'I use the iron-clad Elliptic Curve algorthm to generate the asymmetric keypair.',
        #     '> GenerateKeyPair(KEY_PAIR_TYPE.EC)',
        #     3
        # )
        # self.status(
        #     None,
        #     {ART_KEY_PAIR,True}
        # ) #,clear=False,indent=10,pause=False)
        # self.status(
        #     None,{ART_KEY_PAIR},
        #     'A matching set of keys have been generated.',
        #     None,{ART_KEY_PAIR2A+'\n\nA matching set of keys have been generated.'},
        #     '1)  First, I have made a "public key" which you can share with anyone:',
        #     f'{repr(pubkey)}',
        #     'This key is a randomly-generated binary string, which acts as your "address" on Komrade.',
        #     'By sharing this key with someone, you enable them to write you an encrypted message which only you can read.'
        # )
        # self.status(
        #     None,{ART_KEY_PAIR2A},
        #     f'You can share your public key by copy/pasting it to them over a secure channel (e.g. Signal).',
        #     'Or, you can share it as a QR code, especially phone to phone:',
        #     {qr_str+'\n\n',True,5},
        #     f'\n\n(If registration is successful, this QR code be saved as an image to your device at: {qr_path}.)'
        # )
        
        # private keys
        # self.status(None,
        #     {ART_KEY_PAIR2B},
        #     'Second, I have forged a matching "private key":',
        #     f'{repr(privkey)}',
        #     'With it, you can decrypt any message sent to you via your public key.',
        #     'You you should never, ever give this key to anyone.',
        #     'In fact, this key is so dangerous that I will immediately destroy it by splitting it into two half-keys:'
        # )
        # self.status(None,
        #     {ART_KEY_PAIR31A},
        #     {ART_KEY_PAIR3B+'\n',True},
        #     3,'Allow me to explain.',
        #     '(2A) is a separate encryption key generated by your password.',
        #     '(2B) is a version of (2) which has been encrypted by (2A).',
        #     "Because (2) will be destroyed, to rebuild it requires decrypting (2B) with (2A).",
        # )
        # self.status(
        #     None,{ART_KEY_PAIR5+'\n'},
        #     "However, in a final move, I will now destroy (2A), too.",   
        #     None,{ART_KEY_PAIR4Z1+'\n'},
        #     'Why? Because now only you can regenerate it, by remembering the password which created it.',
        #     # None,{ART_KEY_PAIR4Z1+'\n'},
        #     'However, this also means that if you lose or forget your password, you\'re screwed.',
        #     None,{ART_KEY_PAIR4Z2+'\n'},
        #     "Because without key (2A),you couldn never unlock (2B).",
        #     None,{ART_KEY_PAIR4Z3+'\n'},
        #     "And without (2B) and (2A) together, you could never re-assemble the private key of (2).",
        #     None,{ART_KEY_PAIR4Z42+'\n'},
        #     "And without (2), you couldn't read messages sent to your public key.",
            
        )
        self.status(
            None,{ART_KEY_PAIR4Z1},
            'So choosing a password is an important thing!'
        )
            
        if not passphrase:
            self.status(
                'And it looks like you haven\'t yet chosen a password.',
                3,"Don't tell it to me! Never tell it to anyone.",
                "Ideally, don't even save it on your computer; just remember it, or write it down on paper.",
                "Instead, whisper it to Komrade @Hasher, who scrambles information '1-way', like a blender.",
            )
            res = self.status(None,
                {ART_FROG_BLENDER,True},
                "@Keymaker: Go ahead, try it. Type anything to @Hasher.",
                ('str_to_hash',f'@{name}: ',input)
            )
            str_to_hash = res.get('vals').get('str_to_hash')
            hashed_str = hasher(str_to_hash.encode())
            res = self.status(
                '@Hasher: '+hashed_str
            )

            res = self.status(
                '@Keymaker: See? Ok, now type in a password.'
                ('str_to_hash',f'@{name}: ',getpass)
            )
            str_to_hash = res.get('vals').get('str_to_hash')
            hashed_pass1 = hasher(str_to_hash.encode())
            res = self.status(
                '@Hasher: '+hashed_pass1
            )

            res = self.status(
                '@Keymaker: Whatever you entered, it\'s already forgotten. That hashed mess is all that remains.',
                'Now type in the same password one more time to verify it:',
                ('str_to_hash',f'@{name}: ',getpass)
            )
            str_to_hash = res.get('vals').get('str_to_hash')
            hashed_pass2 = hasher(str_to_hash.encode())
            res = self.status(
                '@Hasher: '+hashed_pass2
            )

            if hashed_pass1==hashed_pass2:
                self.status('The passwords matched.')
            else:
                self.status('The passwords did not match.')
            


        














def run_cli():
    cli = CLI()
    cli.run('/register','elon') #'/register',name='elon')

if __name__=='__main__':
    run_cli()
    # asyncio.run(test_async())