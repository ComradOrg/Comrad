import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
from komrade.backend.keymaker import *
from komrade.backend.messages import Message








class KomradeX(Caller):

    def __init__(self, name=None, pubkey=None):
        super().__init__(name=name)
        self.boot(create=False)
        # special?
        if self.name==WORLD_NAME:
            if os.path.exists(PATH_SUPER_SECRET_OP_KEY): 
                print(f'Dare I claim to be the one true @{WORLD_NAME}?')
                with open(PATH_SUPER_SECRET_OP_KEY,'rb') as f:
                    #pass_encr=f.read()
                    opk1,opk2,privkey_decr,privkey_encr = b64dec(f.read()).split(BSEP)
                    privkey_decr_obj = KomradeSymmetricKeyWithoutPassphrase(privkey_decr)
                    privkey_encr_obj = KomradeEncryptedAsymmetricPrivateKey(privkey_encr)
                    self._keychain['privkey_decr']=privkey_decr_obj
                    self._keychain['privkey_encr']=privkey_encr_obj


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



    ## Talking with Operator
    def ring_ring(self,msg,route=None,**y):
        if type(msg)==dict and not ROUTE_KEYNAME in msg:
            msg[ROUTE_KEYNAME]=route
        return super().ring_ring(msg,caller=self,**y)






    ####################################
    ## (1) Logging in and registering ##
    ####################################



    def register(self, name = None, passphrase = None, is_group=None, show_intro=0,show_body=True,logfunc=None):
        # global PHONEBOOK
        
        # print('got name:',name)
        ## Defaults
        if name and not self.name: self.name=name
        if not name and self.name: name=self.name
        # if not name and not self.name: name=''
        # print('got name',name)
        if not logfunc: logfunc=self.log

        # already have it?
        if self.exists_locally_as_account():
            return {'success':False, 'status':'You have already created this account.'}
        
        if self.exists_locally_as_contact():
            return {'success':False, 'status':'This is already a contact of yours'}

        
        ## 1) Have name?
        clear_screen()
        tolog=''
        if SHOW_STATUS and show_intro:
            self.name = name = self.cli.status_keymaker_part1(name)
        elif not name:
            self.name = name = input('\nHello, this is Komrade @')
            logfunc('I would like to sign up for the socialist network revolution.',flush=True,komrade_name=name,pause=True)
            # do_pause()
        else:
            logfunc(f'Hello, this is Komrade @{name}.\n\nI would like to sign up for the socialist network revolution.',pause=True,komrade_name=name)
            # do_pause()
        
        # clear_screen()
        logfunc(f'Excellent. But to communicate with komrades securely, you must first cut your public & private encryption keys.',pause=True,clear=True)
        # do_pause()
        ## 2) Make pub public/private keys
        keypair = KomradeAsymmetricKey()
        pubkey,privkey = keypair.pubkey_obj,keypair.privkey_obj
        logfunc(f'I have cut for you a private and public asymmetric key pair, using the iron-clad Elliptic curve algorithm:\n\n(1) {pubkey}\n\n(2) {privkey}{ART_KEY_PAIR}',clear=True,pause=True)
        self._keychain['pubkey']=pubkey
        self._keychain['privkey']=privkey
        self.log('My keychain now looks like:',dict_format(self.keychain()))


        ### PUBLIC KEY
        qr_str=self.qr_str(pubkey.data_b64)
        logfunc(f'(1) You may store your public key both on your device hardware, as well as share it with anyone you wish:\n\n{pubkey.data_b64_s}\n\nIt will also be stored as a QR code on your device:\n{qr_str}',pause=True,clear=True)
        logfunc('You must also register your username and public key with Komrade @Operator on the remote server.\n\nShall Komrade @Telephone send them over?',pause=False,clear=False)#),dict_format(data,tab=2),pause=True)
        ok_to_send = input(f'\n@{name}: [Y/n] ')
        if ok_to_send.strip().lower()=='n':
            logfunc('Cancelling registration.')
            return
        else:
            print()
            logfunc('Connecting you to the @Operator...',komrade_name='Telephone')
            # print()
            # time.sleep(1)

        ## CALL OP WITH PUBKEY
        resp_msg_d = self.ring_ring(
            {
                'name':name, 
                'pubkey': pubkey.data,
            },
            route='register_new_user'
        )
        # print()
        clear_screen()
        logfunc(resp_msg_d.get('status')+ART_OLDPHONE4,komrade_name='Operator',pause=True)
        print()

        if not resp_msg_d.get('success'):
            logfunc('''That's too bad. Cancelling registration for now.''',pause=True,clear=True)
            return

        # clear_screen()
        logfunc('Great. Komrade @Operator now has your name and public key on file (and nothing else!).',pause=True,clear=True)

        logfunc(f"(2) Your PRIVATE key, on the other hand, must be stored only on your device hardware.",pause=True)
        logfunc('''Your private key is so sensitive we'll even encrypt it before storing it.''',pause=True,use_prefix=False)

        

        ## 3) Have passphrase?
        if SHOW_STATUS and not passphrase:
            passphrase = self.cli.status_keymaker_part2(name,passphrase,pubkey,privkey,hasher,self)
        else:
            if not passphrase: passphrase = DEBUG_DEFAULT_PASSPHRASE
            while not passphrase:
                # logfunc('Please type a password:',use_prefix=False)
                logfunc('''Please enter a memorable password to generate a (symmetric AES) encryption key with:''',use_prefix=True)
                passphrase=getpass(f'\n@{self.name}: ')
                # clear_screen()
        ## 4) Get hashed password
        
        passhash = hasher(passphrase)
        privkey_decr = KomradeSymmetricKeyWithPassphrase(passhash=passhash)
        print()
        logfunc(f'''Let's immediately run whatever you typed through a 1-way hashing algorithm (SHA-256), inflating it to (redacted):\n\n{make_key_discreet_str(passhash)}''',pause=True,clear=False)

        privkey_encr = privkey_decr.encrypt(privkey.data)
        privkey_encr_obj = KomradeEncryptedAsymmetricPrivateKey(privkey_encr)
        self._keychain['privkey_encr']=privkey_encr_obj
        self.log('My keychain now looks like v2:',dict_format(self.keychain()))

        logfunc('With this inflated password we can encrypt your super-sensitive private key.',pause=True,clear=True)

        logfunc(f"Your original private key looks like this (redacted):\n\n{privkey}",pause=True,clear=False)
        
        logfunc(f"After we encrypt it with your passworded key, it looks like this (redacted):\n\n{privkey_encr_obj}",pause=True,clear=False)

        logfunc('Only this encrypted version is stored.',pause=True,clear=True)


        

        # More narration?
        if SHOW_STATUS: self.cli.status_keymaker_part3(privkey,privkey_decr,privkey_encr,passphrase)
        

        self.name=resp_msg_d.get('name')
        pubkey_b = resp_msg_d.get('pubkey')
        assert pubkey_b == pubkey.data
        uri_id = pubkey.data_b64
        sec_login = resp_msg_d.get('secret_login')
        # stop
        
        logfunc(f'''Saving keys to device:''',pause=True)
        logfunc(f'''(1) {pubkey}''',pause=True,use_prefix=False)
        logfunc(f'''(2) {privkey_encr_obj}''',pause=True,use_prefix=False)
        logfunc(f'''(3) [Shared Login Secret with @Operator]\n({make_key_discreet(sec_login)})''',pause=True,use_prefix=False)
        # print()
        self.crypt_keys.set(name, pubkey_b, prefix='/pubkey/')
        self.crypt_keys.set(uri_id, name, prefix='/name/')
        self.crypt_keys.set(uri_id,sec_login,prefix='/secret_login/')

        # store privkey pieces
        self.crypt_keys.set(uri_id, privkey_encr_obj.data, prefix='/privkey_encr/')
        # just to show we used a passphrase -->
        self.crypt_keys.set(uri_id, KomradeSymmetricKeyWithPassphrase.__name__, prefix='/privkey_decr/')


        # save qr too:
        _fnfn=self.save_uri_as_qrcode(uri_id)
        logfunc(f'Also saving public key as QR code to: {_fnfn}.',pause=True,clear=False,use_prefix=False)
        
        # done!
        print()
        logfunc(f'Congratulations. Welcome, {self}.',pause=True,clear=True)
        # self.help()


        ##
        # last minute: get posts
        if 'res_posts' in resp_msg_d and resp_msg_d['res_posts'].get('success'):
            id2post=resp_msg_d.get('res_posts').get('posts',{})
            if id2post:
                self.log('found starter posts:',list(id2post.keys()))
            self.save_posts(id2post)
            resp_msg_d['status']+=f'  You\'ve got {len(id2post)} new posts and 0 new messages.'
        
        return resp_msg_d


        ###




        return resp_msg_d


    @property
    def secret_login(self):
        return self.crypt_keys.get(
            self.pubkey.data_b64,
            prefix='/secret_login/'
        )

    def login(self,passphrase=None):
        # what keys do I have?
        keys = self.keychain()

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
        resp_msg_d = self.ring_ring(
            msg,
            route='login'
        )

        # print('got resp_msg_d:',resp_msg_d)

        # get result
        self.log('Got resp_msg_d back from operator:',resp_msg_d)

        # check msgs?
        if 'inbox' in resp_msg_d:
            self.do_check_msgs(resp_msg_d['inbox'])
            resp_msg_d['res_refresh'] = self.refresh(check_msgs=False) # already done in previous line

        self.log('-->',resp_msg_d)
        return resp_msg_d















    ########################
    ## (2) MEETING PEOPLE ##
    ########################

    def contacts(self):
        # who do I know?
        return sorted([fn.split('.png')[0] for fn in os.listdir(PATH_QRCODES)])


    ### MEETING PEOLPE
    def meet(self,name=None,pubkey=None,returning=False):
        if not name and not pubkey:
            return {'success':False,'status':'Meet whom?'}
        
        # already met this person?
        keystr=self.name+'->'+name
        # if self.crypt_keys.get(
        #     keystr,
        #     prefix='/met/'
        # ):
        #     return {
        #         'success':False,
        #         'status':f'You have already sent an introduction to @{name}. It would be rude to send another.'
        #     }

        # send msg to op
        msg_to_op = {
            'name':self.name,
            'secret_login':self.secret_login,
            'pubkey':self.uri,

            'meet_name':name,
            'meet_pubkey':pubkey,
            'returning':returning
        }
        self.log('msg_to_op',msg_to_op)

        res = self.ring_ring(
            msg_to_op,
            route='introduce'
        )
        self.log('res from op <-',res)

        # record that I've already tried this
        # self.crypt_keys.set(
        #     keystr,
        #     b'y',
        #     prefix='/met/'
        # )

        # return result
        succ=res.get('success')
        if succ:
            msgd=res.get('msg_d',{})
            msg=msgd.get('msg',{}).get('txt','[?]')
            toname=msgd.get('to_name')
            status = f"""I sent the following message to {toname}:\n\n"{msg}" """
        else:
            status = res.get('status')
        return {
            'status':status,
            'success':succ,
            'res':res
        }


















    ###################
    ## (3) MESSAGING ##
    ###################




    
    def msg(self,someone,something):
        # find or boot
        someone = Komrade(someone)
        self.log(f'found {someone}')
        
        # can we?
        if not someone.pubkey:
            self.log(f'''Don't know the public key of {someone}!''')

        # write them message
        msg_obj = self.compose_msg_to(
            something,
            someone
        )
        self.log('composed msg:',msg_obj)
        
        # encrypt it
        msg_obj.encrypt()

        # attaching
        direct_msg_data = msg_obj.msg
        self.log('going to send only this to op:',direct_msg_data)

        # enclosing
        msg_to_op = {
            'deliver_msg': {
                'from':self.pubkey.data_b64,
                'from_name':self.name,
                'to':someone.pubkey.data_b64,
                'to_name':someone.name,
                'msg':direct_msg_data,
            }
            
        }
        self.log('going to send msg to op?',msg_to_op)
        
        # dial operator
        res=self.ring_ring(
            msg_to_op,
            route='deliver_msg'
        )
        self.log('-->',res)
        return res

    #def post(self,something):
    #    return self.msg(WORLD_NAME,something)
    
    def post(self,something):
        # sign it!
        self.log('something =',something)

        something_b = pickle.dumps(something)
        self.log('something_b =',something_b)

        something_b_signed = ssign(
            self.privkey.data,
            something_b
        )
        self.log('something_b_signed =',something_b_signed)

        # something_b_signed_b64 = b64enc(
        #     something_b_signed
        # )
        # self.log('something_b_signed_b64 =',something_b_signed_b64)

        # encrypt package to world (or op?)
        world=Komrade(WORLD_NAME)
        something_b_signed_encr4world = SMessage(
            self.privkey.data,
            world.pubkey.data
        ).wrap(something_b_signed)
        self.log(something_b_signed_encr4world)
        
        
        post_pkg_d = {
            'post':something_b_signed_encr4world,
            'post_from':self.uri,
            'post_from_name':self.name
        }
        self.log('post_pkg_d =',post_pkg_d)

        post_pkg_b = pickle.dumps(post_pkg_d)
        self.log('post_pkg_b =',post_pkg_d)

        # post_pkg_b_encr4world = SMessage(
        #     self.privkey.data,
        #     Komrade(WORLD_NAME).pubkey.data
        # ).wrap(post_pkg_b)
        # self.log(post_pkg_b_encr4world)

        res_op = self.ring_ring(
            {
                'data':post_pkg_b
            },
            route='post'
        )
        self.log('post res from Op <-',res_op)
        return res_op

    
    @property
    def login_details(self):
        return {
            'name':self.name,
            'secret_login':self.secret_login,
            'pubkey':self.uri
        }

    def save_posts(self,
            id2post,
            inbox_prefix='/feed/',
            post_prefix='/post/'):
        
        # update inbox
        new_inbox = list(id2post.keys())
        self.log('new_inbox ->',new_inbox,inbox_prefix,post_prefix)
        inbox = self.get_inbox_crypt(
            prefix=inbox_prefix
        )
        inbox.prepend(new_inbox)
        self.log('new vals =',inbox.values)

        # update posts
        for post_id,post in id2post.items():
            self.log(f'saving post! --> {post_prefix}{post_id} --> {post}')

            self.crypt_data.set(
                post_id,
                post,
                prefix=post_prefix,
                override=True
            )
            
        res = {
            'success':True,
            'status':f'Saved {len(id2post)} posts.'
        }

        self.log('-->',res)
        return res


    def save_msgs(self,id2msg):
        return self.save_posts(
            id2post=id2msg,
            inbox_prefix='/inbox/',
            post_prefix='/post/'
        )

    ## Getting updates
    def get_updates(self,include_posts=True):
        # get any parameters we need
        post_ids_read = list(self.inbox_read_db.values)

        # compose msg
        msg_to_op = {
            **self.login_details,
            **{'post_ids_read':post_ids_read}
        }
        self.log('msg to op ->',msg_to_op)

        res = self.ring_ring(
            msg_to_op,
            route='get_updates'
        )
        self.log('<- Op.get_updates <-',res)

        # error?
        if not res.get('success'): return res

        # (2) save msgs
        id2msg=res.get('res_msgs').get('posts',{})
        
        # (3) save posts
        if include_posts:
            id2post=res.get('res_posts').get('posts',{})

            # save them: but posts arent msgs!
            # @hack! why is this happening?
            id2msg = dict([(k,v) for k,v in id2msg.items() if k not in id2post])
            

        self.log(f'downloaded {len(id2msg)} messages:',list(id2msg.keys()))
        if include_posts:
            self.log(f'downloaded {len(id2post)} posts:',list(id2post.keys()))

        self.save_msgs(id2msg)
        if include_posts:
            self.save_posts(id2post)

        # return {
        #     'status':f'Retrieved {len(id2post)} posts and {len(id2msg)} messages.',
        #     'id2msg':id2msg,
        #     'id2post':id2post
        # }
        #res['status']=''
        #if len(id2post) or len(id2msg):
        #    res['status']=f'You\'ve got {len(id2post)} new posts and {len(id2msg)} new messages.'
        
        _nup=self.num_unread_posts
        _num=self.num_unread_msgs
        res['status']=f'''You have {_nup} unseen post{'s' if _nup!=1 else ''} and {_num} unread msg{'s' if _num!=1 else ''}.'''
        
        return res
    
    @property
    def num_unread_posts(self):
        return len(self.posts(unread=True))

    @property
    def num_posts(self):
        return len(self.posts())

    @property
    def num_unread_msgs(self):
        return len(self.messages(unread=True))

    @property
    def num_msgs(self):
        return len(self.messages())

    
    
    
    def posts(self,
            unread=None,
            inbox_prefix='/inbox/'):
        inbox_prefix='/feed/'
        inbox=self.get_inbox_crypt(prefix=inbox_prefix).values
        read=self.get_inbox_crypt(prefix=inbox_prefix+'read/').values
        self.log('post index<-',inbox)
        self.log('post index read<-',read)

        if unread:
            inbox = [x for x in inbox if not x in set(read)]

        posts=[]
        for post_id in inbox:
            self.log('???',post_id,inbox_prefix)
            res_post = self.read_post(post_id)
            self.log('got post:',res_post)
            if res_post.get('success') and res_post.get('post'):
                post=res_post.get('post')
                post.post_id=post_id
                post.inbox_prefix=inbox_prefix
                posts.append(post)
        return posts

    def read_post(self,post_id,post_encr=None):
        # get post
        if not post_encr:
            post_encr = self.crypt_data.get(
                post_id,
                prefix='/post/'
            )
        self.log('found encrypted post store:',post_encr)
    
        # first from op to me?
        try:
            msg_from_op_b_encr = post_encr
            self.log('!?!?',self.name,self.uri,post_id,'\n',self.privkey)
            msg_from_op_b = SMessage(
                self.privkey.data,
                self.op.pubkey.data
            ).unwrap(msg_from_op_b_encr)
            self.log('decrypted??',msg_from_op_b)
        except (ThemisError,TypeError) as e:
            self.log(f'!!!!! {e} !!!!!')
            return {
                'success':False,
                'status':'Could not decrypt from operator.'
            }

        # decoded?
        msg_from_op = pickle.loads(msg_from_op_b)
        self.log('decoded?',msg_from_op)
        post_signed_b = msg_from_op.get('post')
        post_from_uri = msg_from_op.get('post_from')
        post_from_name = msg_from_op.get('post_from_name')

        # verify!
        try:
            post_b = sverify(
                b64dec(post_from_uri),
                post_signed_b
            )
        except ThemisError:
            return {'success':False,'status':'Verification failed'}

        # decode
        post_data = pickle.loads(post_b)

        # pretend its a message to world?
        post_obj = Message(
            {
                'from':post_from_uri,'from_name':post_from_name,
                'to':Komrade(WORLD_NAME).uri, 'to_name':WORLD_NAME,
                'msg':post_data
            }
        )
        self.log('post obj?',post_obj)
        post_obj.post_id = post_id
        return {
            'success':True,
            'post':post_obj
        }

    def messages(self,
            unread=None,
            inbox_prefix='/inbox/'):
        # meta inbox
        self.log('<--',inbox_prefix,'???')

        inbox_db=self.get_inbox_crypt(prefix=inbox_prefix)
        read_db=self.get_inbox_crypt(prefix=inbox_prefix+'read/')

        inbox = inbox_db.values
        read = read_db.values
        self.log('<- inbox',inbox)
        self.log('<- read',read)

        # filter?
        if unread:
            inbox = [x for x in inbox if not x in set(read)]
        
        # decrypt and read all posts
        msgs=[]
        for post_id in inbox:
            # self.log('???',post_id,inbox_prefix)
            res_msg = self.read_msg(post_id)
            # self.log('got msg:',res_msg)
            if res_msg.get('success') and res_msg.get('msg'):
                msgx=res_msg.get('msg')
                msgx.post_id=post_id
                msgx.inbox_prefix=inbox_prefix
                msgs.append(msgx)
        return msgs

    def seen_msg(self,msg_or_post):
        # read_msgs = self.get_inbox_crypt(
        #     uri=self.uri,
        #     prefix=msg_or_post.inbox_prefix + 'read/'
        # )
        inbox_prefix=msg_or_post.inbox_prefix
        self.log('inbox_prefix',inbox_prefix)
        read_db=self.get_inbox_crypt(prefix=inbox_prefix+'read/')
        self.log('read_db.values 1',read_db.values)
        read_db.append(msg_or_post.post_id)
        self.log('read_db.values 2',read_db.values)


    def read_msg(self,post_id=None,post_encr=None):
        # get post
        if not post_encr:
            post_encr = self.crypt_data.get(
                post_id,
                prefix='/post/'
            )
        self.log('found encrypted post store:',post_encr)
    
        # first from op to me?
        try:
            msg_from_op_b_encr = post_encr
            self.log('!?!?',self.name,self.uri,post_id,'\n',self.privkey)
            msg_from_op_b = SMessage(
                self.privkey.data,
                self.op.pubkey.data
            ).unwrap(msg_from_op_b_encr)
            self.log('decrypted??',msg_from_op_b)
        except (ThemisError,TypeError) as e:
            self.log(f'!!!!! {e} !!!!!')
            return {
                'success':False,
                'status':'Could not decrypt from operator.'
            }

        # decoded?
        msg_from_op = pickle.loads(msg_from_op_b)
        self.log('decoded?',msg_from_op)

        self.log('msg_from_op is now',msg_from_op)

        # this really to me?
        if msg_from_op.get('to_name') != self.name:
            if msg_from_op.get('to_name') == WORLD_NAME:
                return {
                    'success':True,
                    'msg':Message(msg_from_op)
                }
            else:
                # print(msg_from_op)
                raise KomradeException('Why am I getting this msg? '+str(msg_from_op))
                return

        # now try to decrypt?
        msg2me = Message(
            to_whom=self,
            msg_d={
                'from':msg_from_op.get('from'),
                'from_name':msg_from_op.get('from_name'),
                'msg': msg_from_op.get('msg')
            }
        )
        self.log('msg2me is now v1',msg2me,msg2me.is_encrypted,msg2me.has_embedded_msg)

        if not msg2me.is_encrypted:
            return {
                'success':True,
                'msg':msg2me
            }

        try:
            msg2me.decrypt()
            self.log('msg2me is now v2',dict_format(msg2me.msg_d))
        except ThemisError as e:
            self.log('decryption failuire!!!')
            return {
                'success':False,
                'status':f'De/encryption failure: {e}'
            }

        msg2me.post_id=post_id
        return {
            'success':True,
            'msg':msg2me
        }












    
        
































def test_register():
    import random
    num = random.choice(list(range(0,1000)))
    botname=f'marx{str(num).zfill(3)}'
    marxbot = Komrade(botname)
    # marxbot=Komrade()
    marxbot.register(passphrase='boo')



def test_msg():
    b = Komrade('bez')
    b.inbox()
    # b.read_msg(b'YWY3NDUxZjNjYjdhNDFmNmIyNDI2NzU3YTI4ZTA0OWM=')
    #b.login()

    #print(b.download_msgs())

    # z = Komrade('zuckbot')
    
    # b.msg(z,'you ssssssuck')


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

def test_sign():
    from pythemis import smessage

    b = Komrade('bez')
    m = Komrade('marx')
    z = Komrade('zuckbot')

    msg = b'this is cool. --bez'

    signed_msg = smessage.ssign(b.privkey.data, msg)

    print(signed_msg)

    verified_msg = smessage.sverify(b.pubkey.data, signed_msg)
    print(verified_msg)

def test_send():
    z = Komrade('zuckbot')

if __name__=='__main__':
    test_msg()