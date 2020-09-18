"""
There is only one operator!
Running on node prime.
"""
# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *
from komrade.backend.messages import Message

# print(PATH_OPERATOR_WEB_KEYS_URL)

# def TheOperator(*x,**y):
#     from komrade.backend.operators import Komrade
#     return Komrade(OPERATOR_NAME,*x,**y)

class TheOperator(Operator):
    """
    The remote operator
    """
    @property
    def phone(self):
        global TELEPHONE
        from komrade.backend.the_telephone import TheTelephone
        if not TELEPHONE: TELEPHONE=TheTelephone()
        return TELEPHONE
    

    def __init__(self, name = OPERATOR_NAME, passphrase=None):
        """
        Boot up the operator. Requires knowing or setting a password of memory.
        """

        super().__init__(
            name,
            path_crypt_keys=PATH_CRYPT_OP_KEYS,
            path_crypt_data=PATH_CRYPT_OP_DATA
        )
        from komrade.backend.phonelines import check_phonelines
        keychain = check_phonelines()[OPERATOR_NAME]
        self._keychain = {**self.load_keychain_from_bytes(keychain)}

        if not keychain.get('pubkey'):
            raise KomradeException('Operator cannot find its own public key? Shutting down.')

        # check I match what's on op page
        pub_web = komrade_request(PATH_OPERATOR_WEB_KEYS_URL)
        if pub_web.status_code!=200:
            raise KomradeException("Can't verify Komrade Operator. Shutting down.")
        
        # print('Public key on komrade.app/pub:   ',pub_web.text)
        # print('Public key hardcoded in client:  ',keychain.get('pubkey').data_b64_s)
        
        if pub_web.text == keychain.get('pubkey').data_b64_s:
            # print('Pubs match')
            pass
        else:
            raise KomradeException('Public key for Operator on app and one at {PATH_OPERATOR_WEB_KEYS_URL} do not match. Shutting down.')

        if os.path.exists(PATH_SUPER_SECRET_OP_KEY): 
                print('Dare I claim to be the one true Operator?')
                with open(PATH_SUPER_SECRET_OP_KEY,'rb') as f:
                    #pass_encr=f.read()
                    privkey_decr,privkey_encr,wk1,wk2 = b64dec(f.read()).split(BSEP)
                    privkey_decr_obj = KomradeSymmetricKeyWithoutPassphrase(privkey_decr)
                    privkey_encr_obj = KomradeEncryptedAsymmetricPrivateKey(privkey_encr)
                    self._keychain['privkey_decr']=privkey_decr_obj
                    self._keychain['privkey_encr']=privkey_encr_obj

        self._keychain = {**self.keychain()}
        # self.log('@Operator booted with keychain:',dict_format(self._keychain))
        # clear_screen()

        
        

    def ring(self,
        from_caller=None,
        to_caller=None,
        json_phone2phone={}, 
        json_caller2phone={},   # (person) -> operator or operator -> (person)
        json_caller2caller={}):
        
        encr_msg_to_send = super().ring(
            from_phone=self,
            to_phone=self.phone,
            from_caller=from_caller,
            to_caller=to_caller,
            json_phone2phone=json_phone2phone, 
            json_caller2phone=json_caller2phone,   # (person) -> operator
            json_caller2caller=json_caller2caller)

        return self.send(encr_msg_to_send)

    # ends the ring_ring() chain
    def answer_phone(self,data_b):
        # route incoming call from the switchboard
        from komrade.cli.artcode import ART_OLDPHONE4
        

        self.log(f'''Hello, this is the Operator.{ART_OLDPHONE4}I heard you say:\n\n {b64enc_s(data_b)}''')
        #woops
        # unseal
        # self.log('got:',data_b)
        msg_d = {
            'msg':data_b,
            'from_name':self.phone.name,
            'from':self.phone.pubkey.data,
            'to_name':self.name,
            'to':self.pubkey.data,
        }
        # msg_d = pickle.loads(data_b)
        # self.log('msg_d',msg_d)
        msg_obj = Message(msg_d)
        
        # self.log(f'Decoding the binary, I discovered an encrypted message from {self.phone}\n: {msg_obj}')
        
        # decrypt?
        msg_obj.decrypt()

        # carry out message instructions
        resp_msg_obj = self.route_msg(msg_obj,reencrypt=True) #,route=msg_obj.route)
        self.log('Response from message routing:',resp_msg_obj)

        # send back down encrypted
        # self.log('route msgd',dict_format(resp_msg_obj.msg_d))
        # self.log('route msg',resp_msg_obj.msg)
        # self.log('route msg data',resp_msg_obj.data)
        # self.log('route msg obj',resp_msg_obj)


        
        msg_sealed = pickle.dumps(resp_msg_obj.msg_d)
        # self.log('msg_sealed =',msg_sealed)

        # return back to phone and back down to chain
        return msg_sealed

    def has_user(self,name=None,pubkey=None):
        nm,pk = name,pubkey
        if pubkey: pk=self.crypt_keys.get(
            name,
            prefix='/pubkey/'
        )
        if name: nm=self.crypt_keys.get(
            b64enc(pubkey),
            prefix='/name/'
        )
        self.log(f'checking whether I have user {name} and {pubkey},\n I discovered I had {nm} and {pk} on record')
        # self.log('pks:',pubkey,pk)
        # self.log('nms:',name,nm)
        return (pubkey and pk) or (name and nm)



    def send(self,encr_data_b):
        self.log(type(encr_data_b),encr_data_b,'sending!')
        return encr_data_b

    ### ROUTES
        


        
    def does_username_exist(self,msg_obj):
        data=msg_obj.data
        name=data.get('name')
        pubkey=self.crypt_keys.get(name,prefix='/pubkey/')
        self.log(f'looking for {name}, found {pubkey} as pubkey')
        return bool(pubkey)


    def login(self,msg_obj):
        data=msg_obj.data
        name=data.get('name')
        pubkey=data.get('pubkey')
        secret_login=data.get('secret_login')

        name=name.encode() if type(name)==str else name
        uri = b64enc(pubkey)
        secret_login = b64enc(secret_login)
        name_record = self.crypt_keys.get(
            uri,
            prefix='/name/'
        )
        print(uri,name,name_record,'??')
        pubkey_record = b64enc(self.crypt_keys.get(
            name,
            prefix='/pubkey/'
        ))
        secret_record = b64enc(self.crypt_keys.get(
            uri,
            prefix='/secret_login/'
        ))

        self.log(f'''Checking inputs:
                
        {name} (input)
        vs.
        {name_record} (record)

        {uri} (input)
        vs.
        {pubkey_record} (record)

        {secret_login} (input)
        vs.
        {secret_record} (record)
        ''')
                
        # stop
        # check name?
        if name != name_record:
            self.log('names did not match!')
            success = False 
        # # check pubkey?
        elif uri != pubkey_record:
            self.log('pubkeys did not match!',uri,pubkey_record)
            success = False
        elif secret_login != secret_record:
            self.log('secrets did not match!')
            success = False
        else:
            success = True

        ## return res
        if success:
            return {
                'success': True,
                'status':f'Welcome back, Komrade @{name.decode()}.',
                'status_type':'login',
                'name':name_record.decode(),
                'pubkey':pubkey_record
            }
        else:
            return {
                'success': False,
                'status':'Login failed.',
                'status_type':'login',
            }

    def register_new_user(self,msg_obj):
        # self.log('setting pubkey under name')
        data=msg_obj.data
        name=data.get('name')
        pubkey=data.get('pubkey')

        # is user already there?
        if self.has_user(name=name,pubkey=pubkey):
            return {
                'success':False,
                'status': f"{OPERATOR_INTRO}I'm sorry, but I can't register the name of {name}. This komrade already exists."
            }
        
        # generate shared secret
        shared_secret = get_random_binary_id()
        self.log(f'{self}: Generated shared secret between {name} and me:\n\n{make_key_discreet(shared_secret)}')

        # ok then set what we need
        uri_id = b64enc(pubkey)
        pubkey_b = b64dec(pubkey)
        r1=self.crypt_keys.set(name,pubkey_b,prefix='/pubkey/')
        r2=self.crypt_keys.set(uri_id,name,prefix='/name/')
        # hide secret as key
        r3=self.crypt_keys.set(uri_id,shared_secret,prefix='/secret_login/')

        # success?
        success = r1 and r2 and r3
        if not success:
            return {
                'success':False,
                'status': f"{OPERATOR_INTRO}I'm sorry, but I can't register the name of {name}."
            }

        # save QR also?
        self.save_uri_as_qrcode(uri_id=uri_id,name=name)

        # compose result
        res = {
            'success':success,
            'pubkey':pubkey_b,
            'secret_login':shared_secret,
            'name':name,
            'status':f'Name @{name} was successfully registered.\n\nIt has been permanently linked to the following public key:\n\n{uri_id.decode()}'
        }
        # res_safe = {
        #     **res, 
        #     **{
        #         'secret_login':make_key_discreet(
        #             res['secret_login']
        #         )
        #     }
        # }

        # return
        self.log('Operator returning result:',dict_format(res,tab=4))
        return res
        

        ## success msg
        #
        # cvb64=cv_b64#b64encode(cv).decode()
        # qrstr=self.qr_str(cvb64)
        # res['status']=self.status(f'''{OPERATOR_INTRO}I have successfully registered Komrade {name}.
        
        # If you're interested, here's what I did. I stored the public key you gave me, {cvb64}, under the name of "{name}". However, I never save that name directly, but record it only in a disguised, "hashed" form: {ck}. I scrambled "{name}" by running it through a 1-way hashing function, which will always yield the same result: provided you know which function I'm using, and what the secret "salt" is that I add to all the input, a string of text which I keep protected and encrypted on my local hard drive.
        
        # The content of your data will therefore not only be encrypted, but its location in my database is obscured even to me. There's no way for me to reverse-engineer the name of {name} from the record I stored it under, {ck}. Unless you explictly ask me for the public key of {name}, I will have no way of accessing that information.
        
        # Your name ({name}) and your public key ({cvb64}) are the first two pieces of information you've given me about yourself. Your public key is your 'address' in Komrade: in order for anyone to write to you, or for them to receive messages from you, they'll need to know your public key (and vise versa). The Komrade app should store your public key on your device as a QR code, under ~/.komrade/.contacts/{name}.png. It will look something like this:{qrstr}You can then send this image to anyone by a secure channel (Signal, IRL, etc), or tell them the code directly ({cvb64}).

        # By default, if anyone asks me what your public key is, I won't tell them--though I won't be able to avoid hinting that a user exists under this name should someone try to register under that name and I deny them). Instead, if the person who requested your public key insists, I will send you a message (encrypted end-to-end so only you can read it) that the user who met someone would like to introduce themselves to you; I will then send you their name and public key. It's now your move: up to you whether to save them back your public key.

        # If you'd like to change this default behavior, e.g. by instead allowing anyone to request your public key, except for those whom you explcitly block, I have also created a super secret administrative record for you to change various settings on your account. This is protected by a separate encryption key which I have generated for you; and this key which is itself encrypted with the password you entered earlier. Don't worry: I never saw that password you typed, since it was given to me already hashed and disguised. Without that hashed passphrase, no one will be able to unlock the administration key; and without the administration key, they won't be able to find the hashed record I stored your user settings under, since I also salted that hash with your own hashed passphrase. Even if someone found the record I stored them under, they wouldn't be able to decrypt the existing settings; and if they can't do that, I won't let them overwrite the record.''')
       
        # self.log('Operator returning result:',dict_format(res,tab=2))




    def mass_deliver_msg(self,post_msg_d,contacts):
        def do_mass_deliver_msg(contact,post_msg_d=post_msg_d):
            self.log(f'<- delivering to {contact} the post: {post_msg_d}')
            msg_from_op = Message(
                {  # op -> komrade

                    'to':post_msg_d.get('to'),
                    'to_name':post_msg_d.get('from'),
                    'from':self.uri,
                    'from_name':self.name,
                    'msg':post_msg_d.get             
                }
            )
            self.log(f'prepared msg for {contact}: {msg_from_op.msg}')

            # encrypt
            msg_from_op.encrypt()
            self.log('encrypted to:',msg_from_op.msg)

            # actually deliver
            res=self.actually_deliver_msg(msg_from_op)
            self.log('delivery res =',res)

        for contact in contacts:
            do_mass_deliver_msg(contact)

        return {
            'success':True,
            'status':f'Delivered post to {len(contacts)}.',
        }


    def validate_msg(self,msg_d):
        from komrade.backend.messages import is_valid_msg_d
        if not is_valid_msg_d(msg_d): return False
        
        # alleged
        (
            alleged_to_name,
            alleged_to_pub,
            alleged_from_name,
            alleged_from_pub
        ) = (
            msg_d.get('to_name'),
            msg_d.get('to'),
            msg_d.get('from_name'),
            msg_d.get('from')
        )

        # recorded
        (
            real_to_name,
            real_to_pub,
            real_from_name,
            real_from_pub
        ) = (
            self.find_name(alleged_to_pub),
            self.find_pubkey(alleged_to_name).data_b64,
            self.find_name(alleged_from_pub),
            self.find_pubkey(alleged_from_name).data_b64
        )

        self.log(f'''
        alleged_to_name = {alleged_to_name} 
        alleged_to_pub = {alleged_to_pub}
        alleged_from_name = {alleged_from_name}
        alleged_from_pub = {alleged_from_pub}

        real_to_name = {real_to_name}
        real_to_pub = {real_to_pub}
        real_from_name = {real_from_name}
        real_from_pub = {real_from_pub}
        ''')

        try:
            assert alleged_to_name == real_to_name
            assert alleged_to_pub == real_to_pub
            assert alleged_from_name == real_from_name
            assert alleged_from_pub == real_from_pub
        except AssertionError:
            return False
        return True


    def deliver_msg(self,msg_to_op):
        self.log('<-',msg_to_op)

        data = msg_to_op.data
        self.log('<- data',msg_to_op.data)

        deliver_msg_d = data.get('deliver_msg')
        self.log('<- deliver_msg_d',deliver_msg_d)
        return self.deliver_msg_d(deliver_msg_d)

    def deliver_msg_d(self,deliver_msg_d):
        self.log('<- deliver_msg_d',deliver_msg_d)

        # is valid?
        if not self.validate_msg(deliver_msg_d):
            res = {
                'status':'Message was not valid. Records between Komrade and Operator do not match.',
                'success':False
            }
            self.log('-->',res)

        # encode
        deliver_msg_b = pickle.dumps(deliver_msg_d)
        self.log('<-- deliver_msg_b',deliver_msg_b)

        # encrypt
        deliver_to = b64enc(deliver_msg_d['to'])
        deliver_to_b = b64dec(deliver_to)
        deliver_msg_b_encr = SMessage(
            self.privkey.data,
            deliver_to_b
        ).wrap(deliver_msg_b)
        self.log('<-- deliver_msg_b_encr',deliver_msg_b_encr)

        # actually deliver
        post_id = get_random_binary_id()
        self.crypt_data.set(
            post_id,
            deliver_msg_b_encr,
            prefix='/post/'
        )
        self.log(f'put {deliver_msg_b_encr} in {post_id}')

        # get inbox
        inbox_crypt = self.get_inbox_crypt(
            uri=deliver_to
        )
        self.log('inbox_crypt',inbox_crypt)
        self.log('inbox_crypt.values',inbox_crypt.values)
        res_inbox = inbox_crypt.prepend(post_id)
        self.log('inbox_crypt.values v2',inbox_crypt.values)
        res = {
            'status':'Message delivered.',
            'success':True,
            'post_id':post_id,
            'res_inbox':res_inbox,
            'msg_d':deliver_msg_d
        }
        self.log('->',res)
        return res


    def post(self,msg_to_op):
        # This
        self.log('<--',msg_to_op.msg_d)
        world = Komrade(WORLD_NAME)

        # attached msg
        attached_msg = msg_to_op.msg.get('data')
        self.log('attached_msg =',attached_msg)
        if not attached_msg: return

        # double encrypt it as a message to world
        attached_msg_encr_op2world = SMessage(
            self.privkey.data,
            world.pubkey.data
        ).wrap(attached_msg)

        # just store as the encrypted binary -> world it came in?
        # save
        post_id = get_random_binary_id()
        self.crypt_data.set(
            post_id,
            attached_msg_encr_op2world,
            prefix='/post/'
        )
        self.log(f'put {attached_msg_encr_op2world} in {post_id}')

        # update post index
        post_index = self.get_inbox_crypt(
            uri=WORLD_NAME,
            prefix='/index/'
        )
        self.log('post_index',post_index)
        post_index.prepend(post_id)

        res = {
            'status':'Saved message successfully',
            'success':True,
            'post_id':post_id,
            'msg_saved':attached_msg
        }
        self.log('res =',res)
        return res

    def get_posts(self,msg_to_op,max_posts=25):
        # data
        self.log('<-',msg_to_op)
        data=msg_to_op.data
        self.log('<- data',data)
        seen = set(data.get('seen',[]))
        self.log('seen =',seen)

        # get index
        index = self.get_inbox_crypt(
            uri=WORLD_NAME,
            prefix='/index/'
        )
        self.log('<- index',index)
        post_ids = [x for x in index.values if not x in seen]
        self.log('post_ids =',post_ids)

        # get posts
        world=Komrade(WORLD_NAME)
        id2post={}
        for post_id in post_ids:
            encr_msg_content_op2world = self.crypt_data.get(
                post_id,
                prefix='/post/'
            )
            self.log('<-- encr_msg_content_op2world',encr_msg_content_op2world,'at post id',post_id)
            if not encr_msg_content_op2world: continue

            # decrypt from op
            post_pkg_b = SMessage(
                world.privkey.data,
                self.pubkey.data
            ).unwrap(encr_msg_content_op2world)
            self.log('post_pkg_b',post_pkg_b)

            # decode
            post_pkg_d = pickle.loads(post_pkg_b)
            self.log('post_pkg_d',post_pkg_d)
            from_uri = post_pkg_d.get('post_from')
            from_name = post_pkg_d.get('post_from_name')
            post_b_signed_encr4world = post_pkg_d.get('post')
            # if not from_uri or not from_name or b64enc(self.find_pubkey(from_name))!=from_uri or not post_b_signed_encr4world:
            #     return {
            #         'success':False,
            #         'status':'Records do not match.'
            #     }

            # decrypt from post author komrade
            post_b_signed = SMessage(
                world.privkey.data,
                b64dec(from_uri)
            ).unwrap(post_b_signed_encr4world)
            self.log('post_b_signed',post_b_signed)

            # re-encrypt for the post requester komrade
            post_pkg_d2 = {
                'post':post_b_signed,
                'post_from':from_uri,
                'post_from_name':from_name
            }
            post_pkg_b2 = pickle.dumps(post_pkg_d2)
            post_pkg_b2_encr_op2kom = SMessage(
                self.privkey.data,
                b64dec(msg_to_op.from_pubkey)
            ).wrap(post_pkg_b2)

            # store and return this
            id2post[post_id] = post_pkg_b2_encr_op2kom
        
        res = {
            'status':f'Succeeded in getting {len(id2post)} new posts.',
            'success':True,
            'posts':id2post
        }
        self.log('-->',res)
        return res




    # def deliver_msg(self,msg_to_op):
    #     data = msg_to_op.data
    #     deliver_msg_d = data.get('deliver_msg')

    #     # is valid?
    #     if not self.validate_msg(deliver_msg_d):
    #         res = {
    #             'status':'Message was not valid. Records between Komrade and Operator do not match.',
    #             'success':False
    #         }
    #         self.log('-->',res)

    #     # package
    #     from komrade.backend.messages import Message
    #     msg_from_op = Message(
    #         from_whom=self,
    #         msg_d = {
    #             'to':deliver_msg_d.get('to'),
    #             'to_name':deliver_msg_d.get('to_name'),
    #             'msg':deliver_msg_d
    #         }
    #     )
    #     self.log(f'{self}: Prepared this msg for delivery:\n{msg_from_op}\n\n{dict_format(msg_from_op.msg_d)}')

    #     # encrypt
    #     msg_from_op.encrypt()
    #     self.log("Here's what it looks like before I actually_deliver it",dict_format(msg_from_op.msg_d))

    #     # deliver
    #     return self.actually_deliver_msg(msg_from_op)

    # def actually_deliver_msg(self,msg_from_op):
    #     self.log('msg_from_op <-',msg_from_op)
    #     self.log('msg_from_op.msg_d <-',msg_from_op.msg_d)
    #     self.log('msg_from_op.msg_b <-',msg_from_op.msg_b)
    #     self.log('msg_from_op.msg <-',msg_from_op.msg)
        
    #     msg_from_op_b_encr = msg_from_op.msg     #.msg_b  # pickle of msg_d
    #     self.log('msg_from_op_b_encr <-',msg_from_op_b_encr)
    #     deliver_to = b64enc(msg_from_op.to_pubkey)
    #     deliver_to_b = b64dec(deliver_to)

    #     # save new post
    #     post_id = get_random_binary_id()
    #     self.crypt_data.set(
    #         post_id,
    #         msg_from_op_b_encr,
    #         prefix='/post/'
    #     )
    #     self.log(f'put {msg_from_op} (or {msg_from_op_b_encr}) in {post_id}')

    #     # get inbox
    #     inbox_crypt = self.get_inbox_crypt(
    #         uri=deliver_to
    #     )
    #     self.log('inbox_crypt',inbox_crypt)
    #     self.log('inbox_crypt.values',inbox_crypt.values)
    #     res_inbox = inbox_crypt.prepend(post_id)
    #     self.log('inbox_crypt.values v2',inbox_crypt.values)
    #     res = {
    #         'status':'Message delivered.',
    #         'success':True,
    #         'post_id':post_id,
    #         'res_inbox':res_inbox 
    #     }
    #     self.log('->',res)
    #     return res









    ### 
    # LETS SIMPLIFY THIS
    # Komrade -> Op: get_updates()
    # gets new DMs, new posts,
    # both index/inbox and content/body
    ###

    def require_login(self,msg_to_op,do_login=True):
        # logged in?
        if do_login:
            login_res = self.login(msg_to_op)
            return login_res
        else:
            return {
                'success':True,
                'status':'Login not required.',
                'name':msg_to_op.from_name,
                'pubkey':msg_to_op.from_pubkey
            }


    # (0) get updates
    # user enters here
    def get_updates(self,
            msg_to_op=None,
            inbox_uri=None,
            do_login=True,
            include_posts=True):
        self.log('<-',msg_to_op,inbox_uri)

        # uri?
        if not inbox_uri and not msg_to_op:
            return {'success':False, 'status':'Updates for whom?'}
        uri = inbox_uri if inbox_uri else b64enc(msg_to_op.from_pubkey)

        # (1) req login?
        res_login={}
        if do_login:
            if not msg_to_op:
                return {'success':False,'status':'Cannot login outside of message context.'}
            res_login=self.require_login(msg_to_op,do_login=do_login)
            if not res_login.get('success'):
                return {'success':False,'res_login':res_login} 

        # (2) get msgs
        res_msgs = self.get_msgs(uri)
        self.log('res_msgs',res_msgs)

        # (3) get posts
        res_posts={}
        if include_posts:
            res_posts = self.get_posts(msg_to_op)
            self.log('res_posts',res_posts)

        # return
        res={
            'success': True,
            'status': f'You have {len(msgs)} new messages, and {len(posts)} new posts.',
            'res_login':res_login,
            'res_msgs':res_msgs,
            'res_posts':res_posts,
        }
        self.log('-->',res)
        return res
    


    # (1) get inbox
    def get_inbox(self,inbox_uri):
        # ok, then find the inbox?
        self.log('get_inbox <-',inbox_uri)
        inbox=self.get_inbox_crypt(
            uri=b64enc(inbox_uri),
        )
        self.log('<-inbox <-',inbox)
        
        res = {
            'status':'Succeeded in getting inbox.',
            'success':True,
            'inbox':inbox.values if inbox else []
        }

        self.log(f'--> {res}')
        return res

    def get_msgs(self,inbox_uri):
        # (1) get inbox
        inbox_obj=self.get_inbox_crypt(uri=inbox_uri)
        self.log('<-- inbox crypt',inbox_obj)
        inbox=inbox_obj.values
        self.log('<-- inbox crypt values',inbox)

        # (2) get msgs
        id2msg={}
        for post_id in inbox:
            post = self.crypt_data.get(
                post_id,
                prefix='/post/'
            )
            if post:
                id2msg[post_id] = post
        self.log(f'I {self} found {len(id2msg)}')
        res = {
            'status':f'Succeeded in getting {len(id2msg)} new messages.',
            'success':True,
            'posts':id2msg
        }
        self.log(f'--> {res}')
        return res








    ###
    # INTRODUCTIONS/MEETING
    ###

    def introduce(self,msg_to_op):
        # # logged in?
        # self.log('introduce got:',msg_to_op)
        # login_res = self.login(msg_to_op)
        # self.log('introduce got login-res:',login_res)
        # if not login_res.get('success'):
        #     return login_res
        
        data=msg_to_op.data
        self.log('Op sees data:',dict_format(data))
        meet_pubkey = self.crypt_keys.get(
            data.get('meet_name'),
            '/pubkey/'
        )
        if not meet_pubkey:
            return {
                'success':False,
                'status':'Are you sure this komrade exists? If you are, try contacting them by another secure channel and asking for their public key there.'
            }
        
        self.log('found in crypt:',meet_pubkey)
        meet_name = data.get('meet_name')
        meet_uri = b64enc(meet_pubkey)
        meet_from_name = data.get('name')
        meet_from_uri = data.get('pubkey')
        returning = data.get('returning')

        if returning:
            txt=f'''Komrade @{meet_from_name} has agreed to make your acquaintance.\n\nTheir public key is:\n{meet_from_uri.decode()}.'''
        else:
            txt=f'''Komrade @{meet_from_name} would like to make your acquaintance.\n\nTheir public key is:\n{meet_from_uri.decode()}.'''

        # txt_encr = SMessage(
        #     self.privkey.data,
        #     b64dec(meet_uri)
        # ).wrap(txt)
        # self.log('txt -> encr',txt,txt_encr)
        
        deliver_msg_d={
            'to':meet_uri,
            'to_name':meet_name,
            
            'from':self.uri,
            'from_name':self.name,
            
            'msg':txt,

            'type':'prompt',
            'prompt_id':'addcontact'
        }
        
        self.log('deliver_msg_d ->',deliver_msg_d)
        return self.deliver_msg_d(deliver_msg_d)




















def test_op():
    from komrade.backend.the_telephone import TheTelephone

    from getpass import getpass
    op = TheOperator()
    # op.boot()
    
    keychain_op = op.keychain()

    
    phone = TheTelephone()
    # phone.boot()
    keychain_ph = phone.keychain()

    world = Komrade(WORLD_NAME)
    keychain_w = world.keychain()
    
    
    from pprint import pprint
    print('REASSEMBLED OPERATOR KEYCHAIN')
    print(dict_format(keychain_op))
    # stop
    print()

    print('REASSEMBLED TELEPHONE KEYCHAIN')
    print(dict_format(keychain_ph))
    print()
    
    print('REASSEMBLED WORLD KEYCHAIN')
    print(dict_format(keychain_w))
    print()
    
    # print(op.pubkey(keychain=keychain))
    # print(op.crypt_keys.get(op.pubkey(), prefix='/privkey_encr/'))
    # print(op.crypt_keys.get(op.name, prefix='/pubkey_encr/'))
    # print(op.pubkey_)


    # stop
    
    # pubkey = op.keychain()['pubkey']
    # pubkey_b64 = b64encode(pubkey)
    # print(pubkey)

if __name__ == '__main__': test_op()