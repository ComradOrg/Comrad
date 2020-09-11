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
        # self.boot()
        # self.help()

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
        # logo=make_key_discreet_str(logo,chance_redacted=0.1) #.decode()
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
    def status_keymaker_part1(self,name):
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



    def status_keymaker_part2(self,name,passphrase,pubkey,privkey,hasher,persona):
        from getpass import getpass
        # gen what we need
        uri_id = pubkey.data_b64
        qr_str = get_qr_str(uri_id)
        qr_path = os.path.join(PATH_QRCODES,name+'.png')

        # what are pub/priv?
        self.status(
            'I will forge for you two matching keys, part of an "asymmetric" pair.',
            'Please, watch me work.',
            
            None,{tw.indent(ART_KEY,' '*5)+'\n'},
            
            'I use a high-level cryptographic function from Themis, a well-respected open-source cryptography library.',
            'I use the iron-clad Elliptic Curve algorthm to generate the asymmetric keypair.',
            '> GenerateKeyPair(KEY_PAIR_TYPE.EC)',
            3
        )
        self.status(
            None,
            {ART_KEY_PAIR,True}
        ) #,clear=False,indent=10,pause=False)
        self.status(
            None,{ART_KEY_PAIR},
            'A matching set of keys have been generated.',
            None,{ART_KEY_PAIR2A+'\n\nA matching set of keys have been generated.'},
            '1)  First, I have made a "public key" which you can share with anyone:',
            f'{repr(pubkey)}',
            'This key is a randomly-generated binary string, which acts as your "address" on Komrade.',
            'By sharing this key with someone, you enable them to write you an encrypted message which only you can read.'
        )
        self.status(
            None,{ART_KEY_PAIR2A},
            f'You can share your public key by copy/pasting it to them over a secure channel (e.g. Signal).',
            'Or, you can share it as a QR code, especially phone to phone:',
            {qr_str+'\n\n',True,5},
            f'\n\n(If registration is successful, this QR code be saved as an image to your device at: {qr_path}.)'
        )
        
        # private keys
        self.status(None,
            {ART_KEY_PAIR2B},
            'Second, I have forged a matching "private key":',
            f'{repr(privkey)}',
            'With it, you can decrypt any message sent to you via your public key.',
            'You you should never, ever give this key to anyone.',
            'In fact, this key is so dangerous that I will immediately destroy it by splitting it into two half-keys:'
        )
        self.status(None,
            {ART_KEY_PAIR31A},
            {ART_KEY_PAIR3B+'\n',True},
            3,'Allow me to explain.',
            '(2A) is a separate encryption key generated by your password.',
            '(2B) is a version of (2) which has been encrypted by (2A).',
            "Because (2) will be destroyed, to rebuild it requires decrypting (2B) with (2A).",
        )
        self.status(
            None,{ART_KEY_PAIR5+'\n'},
            "However, in a final move, I will now destroy (2A), too.",   
            None,{ART_KEY_PAIR4Z1+'\n'},
            'Why? Because now only you can regenerate it, by remembering the password which created it.',
            # None,{ART_KEY_PAIR4Z1+'\n'},
            'However, this also means that if you lose or forget your password, you\'re screwed.',
            None,{ART_KEY_PAIR4Z2+'\n'},
            "Because without key (2A),you couldn never unlock (2B).",
            None,{ART_KEY_PAIR4Z3+'\n'},
            "And without (2B) and (2A) together, you could never re-assemble the private key of (2).",
            None,{ART_KEY_PAIR4Z42+'\n'},
            "And without (2), you couldn't read messages sent to your public key.",
            
        )
        self.status(
            None,{ART_KEY_PAIR4ZZ},
            'So choosing a password is an important thing!'
        )
            
        if not passphrase:
            from getpass import getpass
            self.status(
                'And it looks like you haven\'t yet chosen a password.',
                3,"Don't tell it to me! Never tell it to anyone.",
                "Ideally, don't even save it on your computer; just remember it, or write it down on paper.",
                "Instead, whisper it to Komrade @Hasher, who scrambles information '1-way', like a blender.",
            )

            res = self.status(None,
                {indent_str(ART_FROG_BLENDER,10),True},
                "@Keymaker: Go ahead, try it. Type anything to @Hasher.",
                ('str_to_hash',f'@{name}: ',input)
            )
            str_to_hash = res.get('vals').get('str_to_hash')
            hashed_str1 = hasher(str_to_hash.encode())
            res = self.status(
                '@Hasher: '+hashed_str1
            )
            res = self.status(
                '@Keymaker: Whatever you typed, there\'s no way to reconstruct it from that garbled mess.',
                'But whatever you typed will always produce the *same* garbled mess.',
                ('str_to_hash',f'Try typing the exact same thing over again:\n@{name}: ',input)
            )
            str_to_hash = res.get('vals').get('str_to_hash')
            hashed_str2 = hasher(str_to_hash.encode())
            res = self.status(
                '@Hasher: '+hashed_str2
            )
            if hashed_str1==hashed_str2:
                self.status('See how the hashed values are also exactly the same?')
            else:
                self.status('See how the hashed values have also changed?')

            res = self.status(
                ('str_to_hash',f'Now try typing something just a little bit different:\n@{name}: ',input)
            )
            str_to_hash = res.get('vals').get('str_to_hash')
            hashed_str3 = hasher(str_to_hash.encode())
            res = self.status(
                '@Hasher: '+hashed_str3
            )
            if hashed_str2==hashed_str3:
                self.status('See how the hashed values are also the same?')
            else:
                self.status('See how the hashed values have also changed?')


            self.status(
                None,{indent_str(ART_FROG_BLENDER,10)},
                '@Keymaker: Behind the scenes, @Hasher is using the SHA-256 hashing function, which was designed by the NSA.',
                'But @Hasher also adds a secret "salt" to the recipe, as it\'s called.',
                'To whatever you type in, @Hasher adds a secret phrase: another random string of characters which never changes.',
                "By doing so, the hash output is \"salted\": made even more idiosyncratic to outside observers.",
            )

            self.status(
                None,{indent_str(ART_FROG_BLENDER,10)},
                f"I've taken the liberty of generating a random secret for your device, which I show here mostly redacted:",
                make_key_discreet_str(persona.crypt_keys.secret.decode(),0.25),
                'The full version of this secret is silently added to every input you type into @Hasher.',
                "I've saved this secret phrase to a hidden location on your device hardware.",
            )

            self.status(
                None,{indent_str(ART_FROG_BLENDER,10)},
                'However, this means that you will be unable to log in to your account from any other device.',
                'This limitation provides yet another level of hardware protection against network attacks.', 
                'However, you can always choose (not recommended) to the secret file with another device by a secure channel.',
                3,f'But, please excuse me Komrade @{name} -- I digress.'
            )

            while not passphrase:
                res = self.status(None,
                    {indent_str(ART_FROG_BLENDER,10)},
                    "@Keymaker: Please type your chosen password into @Hasher.",
                    ('str_to_hash',f'\n@{name}: ',getpass),
                    pause=False
                )
                str_to_hash = res.get('vals').get('str_to_hash')
                hashed_pass1 = hasher(str_to_hash.encode())
                res = self.status(
                    '\n@Hasher: '+hashed_pass1,
                    pause=False
                )
                res = self.status(
                    '\nNow type in the same password one more time to verify it:',
                    ('str_to_hash',f'\n@{name}: ',getpass),
                    pause=False
                )
                str_to_hash = res.get('vals').get('str_to_hash')
                hashed_pass2 = hasher(str_to_hash.encode())
                res = self.status(
                    '\n@Hasher: '+hashed_pass2,
                    pause=False
                )

                if hashed_pass1==hashed_pass2:
                    self.status('','@Keymaker: Excellent. The passwords clearly matched, because the hashed values matched.',pause=False)
                    passphrase = hashed_pass1
                else:
                    self.status('@Keymaker: A pity. It looks like the passwords didn\'t match, since the hashed values didn\'t match either. Try again?')

            return passphrase

    def status_keymaker_part3(self,privkey,privkey_decr,privkey_encr,passphrase):
        # self.status(
        #     None,{tw.indent(ART_KEY,' '*5)+'\n',True},
        #     # None,{ART_+'\n',True},
        #     'Now that we have a hashed passphrase, we can generate the (2A) encryption key.',
        #     {ART_KEY_KEY2A,True,0.1},
        #     '''This key (2A) is formed using Themis's high-level symmetric encryption key library, SecureCell using Seal mode.''',
        #     '''It uses the AES-256 encryption algorithm, which was developed by the U.S. National Institute of Standards and Technology (NIST) in 2001.'''
        # )
        s1=self.print('Now that we have (2A), we can use it to encrypt the super-sensitive private key (2):',ret=True)
        s2a = self.print(f"(2A) {make_key_discreet_str(passphrase)}",ret=True)
        screen1 = f'''{s1}\n\n{ART_KEY_PAIR_SPLITTING1}\n{s2a}'''

        s2 = self.print(f"(2)  {make_key_discreet(privkey.data_b64)}",ret=True)
        screen2 = f'''{s1}\n\n{ART_KEY_PAIR_SPLITTING2}\n{s2a}\n\n\n{s2}'''

        repr_privkey = repr(privkey).replace('] ',']\n')
        s2b = self.print(f"(2B) {make_key_discreet(b64encode(privkey_encr))}",ret=True)
        screen3 = f'''{s1}\n\n{ART_KEY_PAIR_SPLITTING3}\n{s2a}\n\n\n{s2}\n\n\n{s2b}'''


        self.status(None,s1)
        self.status(None,{screen1})
        do_pause()
        self.status(None,{screen2})
        do_pause()
        self.status(None,{screen3})
        do_pause()












def run_cli():
    cli = CLI()
    cli.run('/register','elon') #'/register',name='elon')

if __name__=='__main__':
    run_cli()
    # asyncio.run(test_async())