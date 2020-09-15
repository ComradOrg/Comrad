import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
import art
import textwrap as tw




class CLI(Logger):
    ROUTES = {
        'help':'seek help',
        'register':'join the komrades',
        'login':'log back in', 
        'meet':'meet a komrade',
        'who':'show contacts or info',
        'msg':'write people',
        'refresh':'refresh mail',
        'read':'read mail',
        'verbose':'show/hide log output'
    }

    def __init__(self,name='',cmd='',persona=None):
        self.name=name
        self.cmd=cmd
        self.komrade=None
        self.loggedin=False

    def verbose(self,*x):
        self.toggle_log()

    def run(self,inp='',name=''):
        # if name: self.name=name
        # clear_screen()
        # self.boot()
        if not inp:
            self.help()

        if inp:
            for inpx in inp.split('/'):
                self.route('/'+inpx.strip())

        while True:
            try:
                inp=input(f'@{self.name if self.name else "?"}: ')
                # print(inp,'??')
                self.route(inp)
            except (KeyboardInterrupt,EOFError) as e:
                exit('\nGoodbye.')
            except KomradeException as e:
                print(f'@Operator: I could not handle your request. {e}\n')
            #await asyncio.sleep(0.5)

    def route(self,inp):
        inp=inp.strip()
        # print('route got:',[inp])
        if not inp.startswith('/'): return
        cmd=inp.split()[0]
        dat=inp[len(cmd):].strip()
        cmd=cmd[1:]
        # print([cmd,dat])
        if cmd in self.ROUTES and hasattr(self,cmd):
            f=getattr(self,cmd)
            return f(dat)

    def boot(self,indent=13):
        logo=art.text2art(CLI_TITLE,font=CLI_FONT)
        # logo=make_key_discreet_str(logo,chance_redacted=0.1) #.decode()
        logo=tw.indent(logo, ' '*indent)
        scan_print(logo,max_pause=0.005)

    def help(self,*x,**y):
        clear_screen()
        self.boot()

        HELPSTR = """
    /login [name]     -->  log back in
    /register [name]  -->  new komrade""" + (("""
    
    /meet [name]      -->  exchange info
    /msg [name] [msg] -->  write to person or group
    /who [name]       -->  show contact info
    
    /refresh [inbox]  -->  refresh messages
    /read [inbox]     -->  read messages""") 
    if self.with_required_login(quiet=True) else "") + """ 
    /help             -->  seek help
"""
        
        print(HELPSTR)

    def intro(self):
        self.status(None)
    
    def who(self,whom):
        if self.with_required_login():
            contacts = self.komrade.contacts()
            print('  ' + '\n  '.join(contacts))

    
    def register(self,name=None):
        if not name: name=input('name: ')
        if not name: return
        self.komrade = Komrade(name)
        res=self.komrade.register()
        if res and type(res)==dict and 'success' in res and res['success']:
            self.name=self.komrade.name
            self.loggedin=True
        else:
            self.name=None
            self.loggedin=False
            self.komrade=None
        if res and 'status' in res:
            # self.boot()
            print('\n@Operator: '+res.get('status','?')+'\n')


    def login(self,name):
        # print(self,name,self.name,self.komrade,self.loggedin)
        if not name: name=input('name: ')
        if not name: return
        self.komrade=Komrade(name)
        
        res = self.komrade.login()

        if res and type(res)==dict and 'success' in res and res['success']:
            self.name=self.komrade.name
            self.loggedin=True
        else:
            self.name=None
            self.loggedin=False
            self.komrade=None
        if res and 'status' in res:
            self.help()
            print('@Operator: '+res.get('status','?')+'\n')

    @property
    def logged_in(self):
        return (self.loggedin and self.komrade and self.name)

    
    def with_required_login(self,quiet=False):
        if not self.logged_in:
            if not quiet:
                print('@Operator: You must be logged in first.\n')
            return False
        return True

    def meet(self,name):
        
        if not name:
            name=input(f'@Operator: To whom would you like to introduce yourself?\n\n@{self.name}: ')
        if not name: return

        # meet?
        self.komrade.meet(name)

    def msg(self,dat):
        if self.with_required_login():
            name_or_pubkey,msg = dat.split(' ',1)
            self.log(f'Composed msg to {name_or_pubkey}: {msg}')
            msg_obj = self.komrade.msg(
                name_or_pubkey,
                msg
            )
            self.log(f'Sent msg obj to {name_or_pubkey}: {msg_obj}')

    def refresh(self,dat):
        if self.with_required_login():
            res = self.komrade.refresh()
            if not res['success']:
                print(f"@Operator: {res['status']}\n")
            else:
                unr = res.get('unread',[])
                inb = res.get('inbox',[])
                print(f'@Operator: You have {len(unr)} unread messages, with {len(inb)} total in your inbox.\n')

    def read(self,dat):
        if self.with_required_login():
            msgs = self.komrade.inbox()
            if not msgs:
                print('@Operator: No messages.')
            else:
                clear_screen()
                for i,msg in enumerate(msgs):
                    print(f'@Operator: Showing most recent messages first.\n\n\n  Message {i+1} of {len(msgs)}')
                    print(msg)
                    do_pause()
                    clear_screen()
                self.help()


















    




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
            
            f'''@{TELEPHONEname}: I could, but it's not safe yet. Your information could be exposed. You need to cut your encryption keys first.''',

            f'@{name}: Fine, but how do I do that?',
            
            f'@{TELEPHONEname}: Visit the Keymaker.',
            
            clear=False,pause=True)

        ### KEYMAKER
        self.status(None,{tw.indent(ART_KEY,' '*5)+'\n',True},3) #,clear=False,indent=10,pause=False)
        # convo
        self.status(
            f'\n@{name}: Hello, Komrade @Keymaker? I would like help forging a new set of keys.',

            f'@Keymaker: Of course, Komrade @{name}.',
        )

        self.status(
            'I will cut for you two matching keys, part of an "asymmetric" pair.',
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

        return name



    def status_keymaker_part2(self,name,passphrase,pubkey,privkey,hasher,persona):
        from getpass import getpass
        # gen what we need
        uri_id = pubkey.data_b64
        qr_str = get_qr_str(uri_id)
        qr_path = os.path.join(PATH_QRCODES,name+'.png')

        # what are pub/priv?

        # self.status(
        #     None,{ART_KEY_PAIR},
        #     'A matching set of keys have been generated.',
        #     None,{ART_KEY_PAIR2A+'\nA matching set of keys have been generated.'+'\n'},
        #     'First, I have made a "public key" which you can share with anyone:',
        #     f'(1) {pubkey.data_b64.decode()}',
        #     'This key is a randomly-generated binary string, which acts as your "address" on Komrade.',
        #     'With it, someone can write you an encrypted message which only you can read.'
        # )
        # self.status(
        #     None,{ART_KEY_PAIR2A},
        #     f'You can share your public key by copy/pasting it to them over a secure channel (e.g. Signal).',
        #     'Or, you can share it as a QR code, especially IRL:',
        #     {qr_str+'\n\n',True,5},
        #     f'\n\n(If registration is successful, this QR code be saved as an image to your device at: {qr_path}.)'
        # )
        
        # private keys
        self.status(None,
            {ART_KEY_PAIR2B},
            'Second, I have cut a matching "private key".',
            "It's too dangerous to show in full, so here it is 66% redacted:",
            f'(2) {make_key_discreet(privkey.data_b64,0.3)}',
            'With it, you can decrypt and read any message sent to you via your public key.',
            'You can also encrypt and send messages to other people whose public keys you have.',
        )

        # private keys
        self.status(None,
            {CUBEKEY},
            'So if someone were to steal your private key, they could read your mail and forge your signature.'
            'You you should never, ever give your private key to anyone.',
            'In fact, this key is so dangerous that we need to lock it away immediately.',
            "We'll even throw away the key we use to lock this private key with!",
            "How? By regenerating it each time from your password.",
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
        self.status(
            None,{tw.indent(ART_KEY,' '*5)+'\n',True},
            # None,{ART_+'\n',True},
            'Now that we have a hashed passphrase, we can generate the (2A) encryption key.',
            {ART_KEY_KEY2A,True,0.1},
            '''The key is formed using Themis's high-level symmetric encryption library: SecureCell, using Seal mode.''',
            'This key (2A) then uses the AES-256 encryption algorithm to encrypt the super-sensitive private key (2):'
        )

        s0=str.center('[Encryption Process]',CLI_WIDTH)
        s1=s0 + '\n\n' + self.printt('Now that we have (2A), we can use it to encrypt the super-sensitive private key (2):',ret=True)
        s2a = self.printt(f"(2A) {make_key_discreet_str(passphrase)}",ret=True)
        s2 = self.printt(f"(2)  {make_key_discreet(privkey.data_b64)}",ret=True)
        s2b = self.printt(f"(2B) {make_key_discreet(b64encode(privkey_encr))}",ret=True)
        self.status(
            # screen 1
            None,{f'{s1}'},
            False,

            # 2
            None,{f'{s1}\n\n{ART_KEY_PAIR_SPLITTING1}'},
            {s2a,True},
            False,
        
            # 3
            None,{f'{s1}\n\n{ART_KEY_PAIR_SPLITTING2}\n{s2a}'},
            {'\n'+s2,True},
            False,

            # 4
            None,{f'{s1}\n\n{ART_KEY_PAIR_SPLITTING3}\n{s2a}\n\n{s2}'},
            {'\n'+s2b,True},
            False,
        )

        
        shdr=str.center('[Decryption Process]',CLI_WIDTH) + '\n\n' + self.printt('Once we have (2B), we don\'t need (2A) or (2) anymore. We can regenerate them!',ret=True)
        from getpass import getpass
        
        passhash = None

        while passhash!=passphrase:
            res = self.status(
                None,{shdr},False if passhash is None else True,

                ("pass",self.printt(f"Let's try. Re-type your password into @Hasher:",ret=True)+f" \n ",getpass)
            )
        
            passhash = self.persona.crypt_keys.hash(res.get('vals').get('pass').encode())
            if passhash!=passphrase:
                self.status({' Looks like they don\'t match. Try again?'},False)
            

        self.status(
            {' Excellent. We can now regenerate the decryption key:'},False,
            {s2a,True},False,
        )

        # self.status('great')
        # shdr2=
        self.status(
        
            # 2
            None,{f'{shdr}\n\n{ART_KEY_PAIR_SPLITTING1}'},
            {s2a,True},
            False,
        
            # 3
            # None,{f'{s1}\n\n{ART_KEY_PAIR_SPLITTING2}\n{s2a}'},
            # {'\n'+s2,True},
            # False,

            # 4
            None,{f'{s1}\n\n{ART_KEY_PAIR_SPLITTING4}\n{s2a}\n\n\n\n'},
            {'\n'+s2b,True},
            False,
        )








def run_cli(inp):
    cli = CLI()
    cli.run(inp) #'/register elon') #'/register',name='elon')

if __name__=='__main__':
    inp = ' '.join(sys.argv[1:])
    run_cli(inp)
    # asyncio.run(test_async())














"""
Outtakes

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
            'Why? Because now only you can regenerate it by remembering the password which created it.',
            # None,{ART_KEY_PAIR4Z1+'\n'},
            'However, this also means that if you lose or forget your password, you\'re screwed.',
            None,{ART_KEY_PAIR4Z2+'\n'},
            "Because without key (2A),you couldn never unlock (2B).",
            None,{ART_KEY_PAIR4Z3+'\n'},
            "And without (2B) and (2A) together, you could never re-assemble the private key of (2).",
            None,{ART_KEY_PAIR4Z42+'\n'},
            "And without (2), you couldn't read messages sent to your public key.",
            
        )
"""