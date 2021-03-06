import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from comrad import *
from comrad.backend import *
import art,asyncio
import textwrap as tw
import readline,logging
readline.set_completer_delims('\t')
# from tab_completer import tabCompleter
tabber=tabCompleter()
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")
torpy_logger = logging.getLogger('torpy')
logging.getLogger('urllib3').propagate=False
logging.getLogger('shapely').propagate=False
logging.getLogger('pyproj').propagate=False
logging.getLogger('rtree').propagate=False
logging.getLogger('asyncio').setLevel(logging.WARNING)

torpy_logger.propagate=False
from shutil import get_terminal_size

CLI_WIDTH = get_terminal_size().columns
CLI_HEIGHT = get_terminal_size().lines-1

class CLI(Logger):
    ROUTES = {
        'help':'seek help',
        'register':'join the comrades',
        'login':'log back in', 
        'meet':'meet a comrad',
        'who':'show contacts or info',
        'dm':'write people',
        'refresh':'refresh feed/DMs',
        'dms':'read DMs',
        'feed':'read posts',
        'verbose':'show/hide log output',
        'post':'post to world',
        'feed':'fetch posts',
        'exit':'exit comrad',
        'clearnet':'switch to clearnet',
        'tor':'switch to tor',
    }

    def __init__(self,name='',cmd='',persona=None):
        self.name=name
        self.cmd=cmd
        self.comrad=None
        self.loggedin=False
        self.tabber=tabber
        self.log('ROUTES:',self.ROUTES)
        self.hops=[]

        # Routes
        rts=['/'+k for k in self.ROUTES]
        tabber.createListCompleter(rts)
        readline.set_completer(tabber.listCompleter)

        # logging
        from comrad.backend.mazes import MazeWalker
        self.walker=MazeWalker(callbacks=self.callbacks)
        self.torpy_logger = logging.getLogger('torpy')
        self.torpy_logger.propagate=False
        self.torpy_logger.addHandler(self.walker)

        import ipinfo
        ipinfo_access_token = '90df1baf7c373a'
        self.ipinfo_handler = ipinfo.getHandler(ipinfo_access_token)

    def verbose(self,*x):
        self.toggle_log()

    def run(self,inp='',name=''):
        # if name: self.name=name
        clear_screen()
        self.boot()
        if not inp:
            self.help()

        if inp:
            for inpx in inp.split('/'):
                self.route('/'+inpx.strip())

        while True:
            try:
                inp=input(f'\n@{self.name if self.name else "?"}: ')
                # self.print(inp,'??')
                self.route(inp)
            except (KeyboardInterrupt,EOFError) as e:
                self.stat('Goodbye.')
                exit()
            except ComradException as e:
                self.stat(f'I could not handle your request. {e}\n')
            #await asyncio.sleep(0.5)
            self.walker.walk=[] # reset logger's walk?

    def route(self,inp):
        inp=inp.strip()
        # self.print('route got:',[inp])
        if not inp.startswith('/'): return
        cmd=inp.split()[0]
        dat=inp[len(cmd):].strip()
        cmd=cmd[1:]
        # self.print([cmd,dat])
        if cmd in self.ROUTES and hasattr(self,cmd):
            f=getattr(self,cmd)
            try:
                res=f(dat)
            except ComradException as e:
                self.stat('Message not sent.',str(e),'\n')

    def stat(self,*msgs,use_prefix=True,prefix=None,comrad_name=None,pause=False,clear=False,min_prefix_len=12,**kwargs):
        if hasattr(self,'_mapscr') and self._mapscr:
            self._mapscr.endwin()
            self._mapscr=None
            self.hops = []
        
        if not prefix:
            if not comrad_name: comrad_name='Telephone'
            # prefix='Comrad @'+comrad_name+': '
            prefix='@'+comrad_name+': '
        # wrap msg
        total_msg=wrapp(
            *msgs,
            use_prefix=use_prefix,
            prefix=prefix if use_prefix and prefix else '',
            min_prefix_len=min_prefix_len if use_prefix and prefix else 0
        )
        print(total_msg)
        # print()
        if pause: do_pause()
        if clear: clear_screen()

    def print(self,*x):
        print(*x)
        # x=' '.join(str(xx) for xx in x)
        # x=str(x).replace('\r\n','\n').replace('\r','\n')
        # for ln in x.split('\n'):
        # #     #scan_print(ln+'\n\n')
        #     if not ln: print()
        #     for ln2 in tw.wrap(ln,CLI_WIDTH):
        #         print(ln2)
        # # x='\n'.join(tw.wrap(x,CLI_WIDTH))
        # # print(x)

    def boot(self,indent=None,scan=True):
        logo=art.text2art(CLI_TITLE,font=CLI_FONT).replace('\r\n','\n')
        newlogo=[]
        for logo_ln in logo.split('\n'):
            logo_ln = logo_ln.center(CLI_WIDTH,' ')
            newlogo.append(logo_ln)
        newlogo_s='\n'.join(newlogo)
        scan_print(newlogo_s,speed=5) if scan else self.print(newlogo_s)


    def status_str(self,unr,tot):
        read=tot-unr
        return f'({unr}*)' if unr else f'({unr})'
        # return f'({unr}*)' if unr else f'({unr})'
        # return f'{unr}* of {tot}' if tot else str(tot)

    @property
    def post_status_str(self):
        if not self.comrad: return ''
        return self.status_str(
            unr=self.comrad.num_unread_posts,
            tot=self.comrad.num_posts
        )

    @property
    def msg_status_str(self):
        if not self.comrad: return ''
        return self.status_str(
            unr=self.comrad.num_unread_msgs,
            tot=self.comrad.num_msgs
        )

    def clearnet(self,_=''):
        os.environ['COMRAD_USE_CLEARNET'] = '1'
        os.environ['COMRAD_USE_TOR'] = '0'
    def tor(self,_=''):
        os.environ['COMRAD_USE_CLEARNET'] = '0'
        os.environ['COMRAD_USE_TOR'] = '1'
    

    def help(self,*x,**y):
        clear_screen()
        self.boot(scan=False)

        

        if not self.logged_in:
            HELPSTR=f"""
/login [name]    -->     log back in
/register [name] -->     new comrad"""
        else:
            HELPSTR=f"""
/refresh         -->     get new data

/feed            -->     scroll feed {self.post_status_str}
/post            -->     post to all

/dms             -->     see DMs     {self.msg_status_str}
/dm [name]       -->     send a DM
/meet [name]     -->     exchange info
/who [name]      -->     show contacts
"""

        HELPSTR+=f"""
/help            -->     seek help
/exit            -->     exit app
"""
        helpstr = tw.indent(HELPSTR.strip()+'\n\n',' '*11)
        # self.print(helpstr)
        # self.print(border+helpstr+'\n'+self.border)
        lns=[ln.strip() for ln in helpstr.split('\n')]
        maxlen=max([len(ln) for ln in lns])
        for ln in lns:
            for n in range(len(ln),maxlen): ln +=' '
            print(ln.center(CLI_WIDTH))


    def exit(self,dat=''):
        exit('Goodbye.')

    @property
    def border(self):
        border = '-' * CLI_WIDTH # (len(logo.strip().split('\n')[0]))
        border=tw.indent(border, ' '*2)
        return border

    def intro(self):
        self.status(None)
    
    def who(self,whom):
        if self.with_required_login():
            contacts_obj = self.comrad.contacts()
            contacts = [p.name for p in contacts_obj]
            self.print('  ' + '\n  '.join(contacts))


    @property
    def callbacks(self):
        return {
            'torpy_guard_node_connect':self.callback_on_hop,
            'torpy_extend_circuit':self.callback_on_hop,
        }
    
    def callback_on_hop(self,rtr):
        def run_map():
            from worldmap_curses import make_map #,print_map_simple
            # clear_screen()
            if not hasattr(self,'_mapscr') or not self._mapscr:
                self._mapscr = mapscr = make_map()
                mapscr.add_base_map()
                # stop
            else:
                mapscr = self._mapscr
            # return

            # mapscr.stdscr.getch()

            deets = self.ipinfo_handler.getDetails(rtr.ip)

            if rtr.ip not in {hop[0].ip for hop in self.hops}:
                    
                self.hops.append((rtr,deets))
                places = [
                    (_deets.city,tuple(float(_) for _ in _deets.loc.split(',')))
                    for (_rtr,_deets) in [(rtr,deets)]
                ]


                msg = ['@Tor: Hiding your IP by hopping it around the globe:'] + [f'{_deets.city}, {_deets.country_name} ({_rtr.nickname})' for _rtr,_deets in self.hops
                ]
                mapscr.run_print_map(places,msg=msg)
                
            
            # self.stat(
            #     msg,
            #     comrad_name='Tor'
            # )
            # print()
            # input('pausing on callback: '+msg)

        run_map()
        # self._mapscr=None

    
    def register(self,name=None):
        if not name: name=input('name: ')
        if not name: return
        self.comrad = Comrad(name,callbacks=self.callbacks)
        was_off=self.off
        # if was_off: self.show_log()
        def logfunc(*x,comrad_name='Keymaker',**y):
            self.stat(*x,comrad_name=comrad_name,**y)
        
        res=self.comrad.register(logfunc=logfunc)
        # if was_off: self.toggle_log()
        if res and type(res)==dict and 'success' in res and res['success']:
            self.name=self.comrad.name
            self.loggedin=True
            self.help()
            # self.stat(f'Welcome, Comrad @{self.name}.')
        else:
            self.name=None
            self.loggedin=False
            self.comrad=None
            self.help()
            if res and 'status' in res:
                # self.boot()
                self.stat(res.get('status','?'),comrad_name='Operator')


    def login(self,name):
        # self.print(self,name,self.name,self.comrad,self.loggedin)
        if not name: name=input('name: ')
        if not name: return
        self.comrad=commie=Comrad(name,callbacks=self.callbacks)

        if commie.exists_locally_as_account():
            from getpass import getpass
            # pw=getpass(f'\n@Telephone: Welcome back. Your password please?\n@{name}: ')
            pw=getpass(f'password: ')
            commie.keychain(passphrase=pw)
            self.log(f'updated keychain: {dict_format(commie.keychain())}')
            self.log(f'is account')
            # self.login_status.text='You should be able to log into this account.'
            if commie.privkey:
                self.log(f'passkey login succeeded')                
                self.stat(f'Welcome back, Comrad @{commie.name}')
                self.loggedin=True
                self.name=commie.name
                self.help()
            else:
                logger.info(f'passkey login failed')
                self.stat('Login failed...')
        else:
            self.stat('This is not an account of yours.')

        # return self.refresh()
        # res = self.comrad.login()
        # return self.do_login(res)

    def do_login(self,res):
        # print('got login res:',res)
        self.log('<- comrad.login() <-',res)
        
        if res and type(res)==dict and 'success' in res and res['success']:
            self.name=res['name']
            self.comrad=Comrad(res['name'],callbacks=self.callbacks)
            self.loggedin=True
        else:
            self.name=None
            self.loggedin=False
            self.comrad=None
        if res and 'status' in res:
            self.boot(scan=False)
            self.help()
            self.stat(res.get('status','?'),comrad_name='Operator')
        
        return bool(res.get('success'))

    @property
    def logged_in(self):
        return (self.loggedin and self.comrad and self.name)

    
    def with_required_login(self,quiet=False):
        if not self.logged_in:
            if not quiet:
                self.stat('You must be logged in first.')
            return False
        return True


    def meet(self,dat,returning=False):
        if self.with_required_login():
            datl=dat.strip().split()
            if not datl:
                self.stat('Meet whom?')
                return
            name_or_pubkey = datl[0]
            res = self.comrad.meet(name_or_pubkey,returning=returning)
            status=res.get('status')
            self.stat(status)


    def dm(self,dat='',name_or_pubkey=None,msg_s=None):
        if self.with_required_login():

            if not name_or_pubkey:
                dat=dat.strip()
                if not dat:
                    self.status('Message whom? Usage: /msg [name]')
                    return

                datl=dat.split(' ',1)
                name_or_pubkey = datl[0]
            if name_or_pubkey.startswith('@'):
                name_or_pubkey=name_or_pubkey[1:]

            if not msg_s:
                datl=dat.split()
                if len(datl)==1:
                    print()
                    self.stat(f'Compose your message to @{name_or_pubkey} below.', 'Press Ctrl+D to complete, or Ctrl+C to cancel.')
                    print()
                    msg_s = multiline_input().strip()
                    if not msg_s:
                        print('\n')
                        self.stat('Not sending. No message found.')
                        return
                else:
                    msg_s = datl[1]

            self.log(f'Composed msg to {name_or_pubkey}: {msg_s}')
            msg_obj = self.comrad.msg(
                name_or_pubkey,
                msg_s
            )
            self.log(f'Sent msg obj to {name_or_pubkey}: {msg_obj}')
            print()
            self.stat(f'Message successfully sent to @{name_or_pubkey}.',comrad_name='Operator',pause=True)




    def refresh(self,dat=None,res=None,statd={}):
        self.log(f'<-- dat={dat}, res={res}')
        # stop

        ## get updates
        # this does login, msgs, and posts in one req
        time.sleep(0.25)
        if not self.comrad:
            self.stat('You must login first.')

        res = self.comrad.refresh()
        #print(res.get('success'))
        if not res.get('success'):
            self.stat(res.get('status'),comrad_name='')
            return

        # self.stat('Patching you through to the @Operator. One moment please...')
        if hasattr(self,'_mapscr') and self._mapscr:
            #stop
            msg=self._mapscr.msg + ['???, ??? (@Operator)']
            self._mapscr.run_print_map(msg=msg)
            time.sleep(1)
            self._mapscr.endwin()
            self._mapscr=None
            self.hops=[]
        self.log('<-- get_updates',res)
        
        # check logged in
        # res_login=res.get('res_login',{})
        # if not self.do_login(res_login): return
        # self.stat('',res['status'],comrad_name='Operator',**statd)
        self.help()
        return res



    def prompt_adduser(self,msg):
        # self.print('prompt got:',msg)
        # self.print(msg.data)
        do_pause()
        # clear_screen()
        # print(dict_format(msg.data))
        # do_pause()
        meet_name = msg.data.get('meet_name')
        meet_uri = msg.data.get('meet')    
        qrstr=self.comrad.qr_str(meet_uri)
        self.stat(f"Add @{meet_name}'s public key to your address book?",f'It will allow you and @{meet_name} to read and write encrypted messages to one another.')
        do_adduser = input(f'''\n{self.comrad} [y/N]: ''')
        if do_adduser.strip().lower()=='y':
            
            import pyqrcode
            print('meet_uri',meet_uri,'???')
            qr = pyqrcode.create(meet_uri)
            fnfn = os.path.join(PATH_QRCODES,meet_name+'.png') # self.get_path_qrcode(name=name)
            qr.png(fnfn,scale=5)

            clear_screen()
            self.stat(f'The public key of @{meet_name} has been saved as a QRcode to {fnfn}')
            print(qrstr)
            do_pause()
            clear_screen()
        
        # print(msg.data)
        # if not msg.data.get('returning'):
        # bit hacky way to tell if this has been returned or not!
        if 'has agreed' not in msg.data.get('txt',''):
            self.stat('Send this comrad your public key as well?')
            do_senduser = input(f'''\n{self.comrad} [y/N]: ''')

            if do_senduser.strip().lower()=='y':
                res = self.comrad.meet(meet_name,returning=True)
                if res.get('success'):
                    self.log('res?!',res)
                    self.stat('Returning the invitation:',f'"{res.get("res",{}).get("msg_d",{}).get("msg",{}).get("txt","[?]")}"',use_prefix=True)
                    do_pause()
                else:
                    self.stat(msg.get('status'))

    def prompt_msg(self,msg):
        clear_screen()
        print(msg)
        self.stat('Type "r" to reply to this message, "d" to delete it, hit Enter to continue, or type "q" to return to main menu.',use_prefix=False)
        do = input(f'\n{self.comrad}: ')
        do=do.strip().lower()
        if do=='d':
            # self.print('del',msg.post_id)
            res=self.comrad.delete_post(msg.post_id)
            if res.get('success'):
                self.stat('Deleted message.')
            else:
                self.stat('Could not delete message.')
            do_pause()
        elif do=='r':
            # self.print('@todo: replying...')
            return self.dm(msg.from_name)
        elif do=='q':
            raise EOFError
        else:
            # seen this msg!
            self.comrad.seen_msg(msg)
            pass


    def dms(self,dat=''):
        if self.with_required_login():
            msgs=self.comrad.messages()
            return self.read(msgs)

    def feed(self,dat=''):
        if self.with_required_login():
            posts=self.comrad.posts()
            return self.read(posts)

    def read(self,msgs):
        if not msgs:
            self.stat('No messages.')
        else:
            clear_screen()
            for i,msg in enumerate(msgs):
                try:
                    self.stat(f'Showing message {i+1} of {len(msgs)}, from newest to oldest. Hit Ctrl+D to exit.')
                    print()
                    print(msg)
                    self.log('DATA',msg.msg_d)
                    if msg.data.get('prompt_id')=='addcontact':
                        self.prompt_adduser(msg)
                    
                    self.prompt_msg(msg)
                    clear_screen()
                except EOFError:
                    break
            self.help()


    def post(self,dat='',maxlen=MAX_POST_LEN):
        if self.with_required_login():
            self.stat(f'Write your post below. Maximum of 1000 characters.', 'Press Ctrl+D to complete, or Ctrl+C to cancel.')
            print()
            msg_s = multiline_input() #.strip()
            if not msg_s:
                print('\n')
                self.stat('Not sending. No text entered.')
                return
            if len(msg_s)>maxlen:
                msg1=f'Not sending. Message is {len(msg_s)-maxlen} characters over the character limit of {maxlen}.'
                msg2='The message you wanted to send is copied below (in case you want to copy/paste it to edit it):',
                msg3='The message you wanted to send is copied above (in case you want to copy/paste it to edit it).'
                err = f'{msg1}\n\n{msg2}\n\n{msg_s}'
                err2= f'{msg1}\n\n{msg3}'
                print()
                self.stat(msg1)
                # self.stat(err2)
                return

        self.log(f'Post written: {msg_s}')
        msg_obj = self.comrad.post(
            msg_s
        )
        self.log(f'Posted: {msg_obj}')
        print()
        self.stat(f'Post sent to @{WORLD_NAME}.',comrad_name='Operator',pause=True)










    




    ### DIALOGUES

    # hello, op?
    def status_keymaker_part1(self,name):
        self.status(None,{ART_OLDPHONE4+'\n',True},3) #,scan=False,width=None,pause=None,clear=None)
        
        nm=name if name else '?'
        self.status(
            f'\n\n\n@{nm}: Uh yes hello, Operator? I would like to join Comrad, the socialist network. Could you patch me through?',clear=False)

        while not name:
            name=self.status(('name','@TheTelephone: Of course, Comrad...?\n@')).get('vals').get('name').strip()
            self.print()
        
        self.status(
            f'@TheTelephone: Of course, Comrad @{name}. A fine name.',

            '''@TheTelephone: However, I'm just the local operator who lives on your device; my only job is to communicate with the remote operator securely.''',
            
            '''Comrad @TheOperator lives on the deep web. She's the one you want to speak with.''',

            None,{ART_OLDPHONE4},f'''@{name}: Hm, ok. Well, could you patch me through to the remote operator then?''',
            
            f'''@{TELEPHONEname}: I could, but it's not safe yet. Your information could be exposed. You need to cut your encryption keys first.''',

            f'@{name}: Fine, but how do I do that?',
            
            f'@{TELEPHONEname}: Visit the Keymaker.',
            
            clear=False,pause=True)

        ### KEYMAKER
        self.status(None,{tw.indent(ART_KEY,' '*5)+'\n',True},3) #,clear=False,indent=10,pause=False)
        # convo
        self.status(
            f'\n@{name}: Hello, Comrad @Keymaker? I would like help forging a new set of keys.',

            f'@Keymaker: Of course, Comrad @{name}.',
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
        #     'This key is a randomly-generated binary string, which acts as your "address" on Comrad.',
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
                "Instead, whisper it to Comrad @Hasher, who scrambles information '1-way', like a blender.",
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
                3,f'But, please excuse me Comrad @{name} -- I digress.'
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