import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
from komrade.backend.keymaker import *
from komrade.backend.messages import Message








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
            time.sleep(1)

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
        if 'res_check_msgs' in resp_msg_d:
            self.do_check_msgs(resp_msg_d['res_check_msgs'])
            resp_msg_d['res_refresh'] = self.refresh(check_msgs=False) # already done in previous line

        self.log('-->',resp_msg_d)
        return resp_msg_d



    ## MEETING PEOPLE

    def find(self,someone):
        if type(someone)==str:
            return Komrade(name=someone)
        if type(someone)==bytes:
            return Komrade(pubkey=someone)
        self.log('what is type of someoen here?',type(someone))
        return someone

    # def meet(self,someone):
    #     # get person obj
    #     someone = self.find(someone)
    #     self.log('got someone =',someone,type(someone))


    def contacts(self):
        # who do I know?
        return sorted([fn.split('.png')[0] for fn in os.listdir(PATH_QRCODES)])




    def ring_ring(self,msg,route=None,**y):
        if type(msg)==dict and not ROUTE_KEYNAME in msg:
            msg[ROUTE_KEYNAME]=route
        return super().ring_ring(msg,caller=self,**y)


    def fetch_posts(self,n=100,only_from=[],not_from=[]):
        # already seen?
        seen_post_ids_b = self.crypt_keys.get(
            'seen_post_ids',
            prefix='/cache/'
        )
        if seen_post_ids_b:
            seen_post_ids=pickle.loads(seen_post_ids_b)
        else:
            seen_post_ids=[]
        self.log('seen_post_ids =',seen_post_ids)

        # ring operator
        res_b = self.ring_ring(
            {
                'seen_post_ids':seen_post_ids,
                'only_from':only_from,
                'not_from':not_from,
                'n':n
            },
            route='fetch_posts'
        )
        self.log('res_b <-',res_b)

        # msg from world?
        msg_from_world = Message(
            from_whom=self.op,#Komrade(WORLD_NAME),
            to_whom=self,
            msg=res_b
        )
        self.log('converted to msg:',msg_from_world.msg_d)
        msg_from_world.decrypt()
        self.log('decrypted msg:',msg_from_world)

        # get binary blob for all fetched posts
        msgs_d = msg_from_world.msg
        self.log('msgs_d??',msgs_d)
        msgs = msgs_d['msg'].split(BSEP) if msgs_d['msg'] else []

        res = {
            'status':f'Fetched {len(msgs)} poss.',
            'success':True,
            'msgs':msgs
        }

        self.log('->',res)
        return res

    
    # def post(self,something,to_name=WORLD_NAME):
    #     self.log('<-',something,to_name)
    #     # encryption chain:
    #         # me -> world
    #             # me -> op
    #             # op <- me
    #         # op -> others
    #     to_komrade = Komrade(to_name)
    #     self.log('posting to',to_name,to_komrade,to_komrade.uri)
    #     # make post data
        

    #     # encrypt
    #     something_encr = SMessage(
    #         self.privkey.data,
    #         to_komrade.pubkey.data
    #     ).wrap(something)

    #     # make dict (do not use normal msg_d key names!)
    #     post_d = {
    #         'post':{
    #             'from':self.uri,
    #             'from_name':self.name,
    #             'to_name':to_name,
    #             'to':to_komrade.uri,
    #             'msg':something_encr
    #         }
    #     }
    #     self.log('post_d =',post_d)
    #     # enclose as message to operator
    #     self.ring_ring(
    #         post_d,
    #         route='post'
    #     )

    def post(self,something):
        return self.msg(WORLD_NAME,something)
        


    
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
            'deliver_from_name':self.name,
            'deliver_to':someone.pubkey.data_b64,
            'deliver_to_name':someone.name,
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
            'pubkey':self.uri,
            'inbox':inbox
        }
        self.log('sending msg to op:',msg)

        # Ring operator
        res = self.ring_ring(
            msg,
            route='check_msgs'
        )
        self.log('got back response:',res)

        return self.do_check_msgs(res)

    def do_check_msgs(self,res):
        # decrypt?
        if not res.get('data_encr'):
            return {'success':False, 'status':'No data'} 
        inbox_encr = res['data_encr']

        inbox = SMessage(
            self.privkey.data,
            self.op.pubkey.data
        ).unwrap(inbox_encr)
        self.log('inbox decrypted:',inbox)

        # overwrite my local inbox with encrypted one from op?
        return self.crypt_keys.set(
            self.uri,
            inbox,
            prefix='/inbox/',
            override=True
        )

    def refresh(self,check_msgs=True):
        # refresh inbox
        if check_msgs:
            self.check_msgs()

        # status?
        inbox_status = self.get_inbox_ids()
        if not inbox_status['success']: return inbox_status

        unread=inbox_status.get('unread',[])
        inbox=inbox_status.get('inbox',[])
        
        # download new messages
        self.download_msgs(post_ids = inbox)

        res = {
            'success':True,
            'status':'Messages refreshed',
            'unread':unread,
            'inbox':inbox
        }
        self.log('->',res)
        return res

    def save_inbox(self,
            post_ids,
            uri=None,
            encrypted=False):
        self.log('<-',post_ids)
        newval = BSEP.join(post_ids)
        
        res = self.crypt_keys.set(
            self.uri if not uri else uri,
            newval,
            prefix='/inbox/',
            override=True
        )
        assert newval == self.crypt_keys.get(
            self.uri,
            prefix='/inbox/'
        )
        self.log('->',res)
        return res

    def delete_msg(self,post_id):
        return self.delete_msgs([post_id])

    def delete_msgs(self,post_ids):
        inbox_ids = self.get_inbox_ids().get('inbox',[])
        #print(inbox_ids,'v1',len(inbox_ids))
        deleted=[]
        for post_id in post_ids:
            #print('deleting post:',post_id)
            self.crypt_keys.delete(
                post_id,
                prefix='/post/',
            )
            deleted+=[post_id]
        
            #print(post_id,inbox_ids,post_id in inbox_ids,'???')
            # stop
            if post_id in inbox_ids:
                # print('removing from inbox...')
                inbox_ids.remove(post_id)
        self.save_inbox(inbox_ids)
        #print(inbox_ids,'v2',len(inbox_ids))

        res= {
            'success':not bool(set(post_ids) - set(deleted)),
            'status':f'Deleted {len(deleted)} messages.',
            'deleted':deleted
        }
        self.log('delete_msgs ->',res)
        return res

    def inbox(self,topn=100,only_unread=False,delete_malformed=False,check_msgs=False):
        # refreshing inbox
        res = self.refresh(check_msgs=check_msgs)
        # print('got from refresh',res)
        if not res['success']: return res
        
        boxname = 'inbox' if not only_unread else 'unread'
        post_ids = res[boxname]
        msgs=[]
        post_ids_malformed=[]
        for post_id in post_ids:
            malformed = False
            try:
                res = self.read_msg(post_id)
                # print('GOT FROM READ_MSG',res)
            except ThemisError as e:
                print(f'!! Could not decrypt post {post_id}')
                malformed = True

            #print(res,'ressss')
            if not res.get('success'):
                # return res
                continue

            msg=res.get('msg')
            if not msg: continue
            # print(msg,'?!?!??!')
            # stop
            
            if not msg.from_name or not msg.from_pubkey:
                print('!! Invalid sender info!')
                malformed = True

            msg.post_id=post_id

            if not malformed:
                # print('good msg:',msg)
                msgs.append(msg)
            else:
                post_ids_malformed.append(post_id)
            
            if len(msgs)>=topn: break
            # print('!!',post_id,msg.from_whom, msg.to_whom, msg.from_whom is self)

        if delete_malformed:
            self.delete_msgs(post_ids_malformed)

        #print(msgs,'msssgs')
        return {'success':True,
        'msgs':msgs}

        # return all messages read?


    def get_inbox_ids(self):
        inbox = self.crypt_keys.get(
            self.uri,
            prefix='/inbox/',
        )

        # decrypt inbox?
        if inbox:
            inbox = inbox.split(BSEP)
            self.log('inbox_l',inbox)
        else:
            inbox=[]

        # find the unread ones
        unread = []
        for post_id in inbox:
            if not post_id: continue
            if not self.crypt_keys.get(post_id,prefix='/post/'):
                unread.append(post_id)

        self.log(f'I {self} have {len(unread)} new messages')        
        res = {
            'success':True,
            'status':'Inbox retrieved.',
            'unread':unread,
            'inbox':inbox
        }
        self.log('->',res)
        return res
    
    
    def read_msg(self,post_id):
        # get post
        post_encr = self.crypt_keys.get(post_id,prefix='/post/')
        # print(post_id,'????')
        if not post_encr:
            self.download_msgs([post_id])
            post_encr = self.crypt_keys.get(post_id,prefix='/post/')
            # print(post_id,'????')
            
            return {
                'success':False,
                'status':'Post not found.'
            }
        self.log('found encrypted post store:',post_encr)
        # self.log('unpickling?',pickle.loads(post_encr))
        

        # it should be twice decrypted
        msg_op2me_obj = Message(
            from_whom=self.op,
            to_whom=self,
            msg=post_encr
        )
        self.log('assuming this is the message:',msg_op2me_obj)

        # decrypt
        msg_op2me_obj.decrypt()

        # dict to/from/msg
        msg_op2me = msg_op2me_obj.msg.msg_d
        self.log('msg_op2me is now',msg_op2me)

        # this really to me?
        assert msg_op2me.get('to') == self.uri

        # now try to decrypt?
        msg2me = Message(
            to_whom=self,
            msg_d={
                'from':msg_op2me.get('from'),
                'from_name':msg_op2me.get('from_name'),
                'msg': msg_op2me.get('msg')
            }
        )
        # self.log('msg2me is now v1',msg2me)
        msg2me.decrypt()
        self.log('msg2me is now v2',dict_format(msg2me.msg_d))

        return {
            'success':True,
            'msg':msg2me
        }


    
    def download_msgs(self,post_ids=[],inbox=None):
        if not post_ids:
            # get unerad
            post_ids = self.get_inbox_ids().get('unread',[])
        if not post_ids:
            return {'success':False,'status':'No messages requested'}

        # ask Op for them
        res = self.ring_ring(
            {
                'secret_login':self.secret_login,
                'name':self.name,
                'pubkey':self.uri,
                'post_ids':post_ids,
            },
            route='download_msgs'
        )

        # print('got back from op!',res)
        if not 'data_encr' or not res['data_encr'] or type(res['data_encr'])!=dict:
            return {'success':False, 'status':'No valid data returned.'}

        # store -- encrypted!
        posts_downloaded = []
        for post_id,post_encr in res['data_encr'].items():
            # print('storing...',post_id)
            self.crypt_keys.set(
                post_id,
                post_encr,
                prefix='/post/'
            )
            posts_downloaded.append(post_id)
        return {
            'success':True,
            'status':'Messages downloaded',
            'downloaded':posts_downloaded,
        }



    ### MEETING PEOLPE
    def meet(self,name=None,pubkey=None,returning=False):
        if not name and not pubkey:
            return {'success':False,'status':'Meet whom?'}


        keystr=self.name+'->'+name

        # if self.crypt_keys.get(
        #     keystr,
        #     prefix='/met/'
        # ):
        #     return {
        #         'success':False,
        #         'status':f'You have already sent an introduction to @{name}. It would be rude to send another.'
        #     }

        msg_to_op = {
            'name':self.name,
            'secret_login':self.secret_login,
            'pubkey':self.uri,

            'meet_name':name,
            'meet_pubkey':pubkey,
            'returning':returning
        }
        # print('msg_to_op',msg_to_op)

        res = self.ring_ring(
            msg_to_op,
            route='introduce_komrades'
        )
        # print('res from op',res)

        # record that I've already tried this
        self.crypt_keys.set(
            keystr,
            b'y',
            prefix='/met/'
        )

        return res


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