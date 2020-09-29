import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from comrad import *
from screens.base import *
from kivymd.uix.boxlayout import *
from kivymd.uix.textfield import *
from kivymd.uix.button import *
from kivymd.uix.label import *
from kivymd.uix.card import *
from kivy.uix.label import *
from kivymd.uix.dialog import *
from main import *
from misc import *
from kivy.app import *

import logging
logger = logging.getLogger(__name__)

class LoginBoxLayout(MDBoxLayout): pass
class LoginButtonLayout(MDBoxLayout): pass
class UsernameField(MDTextField): pass
class PasswordField(MDTextField): pass
class LoginButton(MDRectangleFlatButton): pass
class RegisterButton(MDRectangleFlatButton,Logger):
    def enter(self):
        un=self.parent.parent.parent.username_field.text
        # pw=self.parent.parent.parent.password_field.text
        login_screen = self.parent.parent.parent

        time.sleep(0.1)
        asyncio.create_task(login_screen.boot(un))

        # logger.info('types',type(self.parent),type(self.parent.parent.parent))
        
        # app=App.get_running_app()
        # app.boot(un)
        # app.change_screen_from_uri(f'/inbox/{un}')
    
    pass
class LoginStatus(MDLabel): pass

class UsernameLayout(MDBoxLayout): pass
class UsernameLabel(MDLabel): pass
class WelcomeLabel(MDLabel): pass

class PasswordPopup(MDDialog): pass

class LoginScreen(BaseScreen): 
    #def on_pre_enter(self):
    #    global app
    #    if app.is_logged_in():
    #        app.root.change_screen('feed')
    def on_pre_enter(self):
        #log(self.ids)
        #log('hello?')
        self.dialog=None
        self.pass_added=False
        self.layout = LoginBoxLayout()
        self.label_title = WelcomeLabel()
        self.label_title.font_name='assets/font.otf'
        # self.label_title.font_size='20sp'
        self.label_title.bold=True
        self.label_title.markup=True
        self.label_title.color=rgb(*COLOR_TEXT)
        self.label_title.text='Welcome,'
        self.layout.add_widget(get_separator('20sp'))
        self.layout.add_widget(self.label_title)
        self.layout.add_widget(get_separator('30sp'))
        # self.layout.add_widget(MySeparator())
        

        self.layout_username = UsernameLayout()
        self.label_username = UsernameLabel(text="Comrad @")

        self.username_field = UsernameField()
        self.username_field.line_color_focus=rgb(*COLOR_TEXT)
        self.username_field.line_color_normal=rgb(*COLOR_TEXT,a=0.25)
        self.username_field.font_name='assets/font.otf'

        self.layout_username.add_widget(self.label_username)
        self.layout_username.add_widget(self.username_field)

        self.layout.add_widget(self.layout_username)
        #log(self.username_field)
        # self.username_field.text='hello????'

        # self.layout_password = UsernameLayout()
        # self.label_password = UsernameLabel(text='password:')

        # self.label_password.font_name='assets/font.otf'
        self.label_username.font_name='assets/font.otf'

        # self.password_field = PasswordField()
        # self.password_field.line_color_focus=rgb(*COLOR_TEXT)
        # self.password_field.line_color_normal=rgb(*COLOR_TEXT,a=0.25)
        # self.password_field.font_name='assets/font.otf'
        
        # self.layout_password.add_widget(self.label_password)
        # self.layout_password.add_widget(self.password_field)
        # self.layout.add_widget(self.layout_password)

        self.layout_buttons = LoginButtonLayout()
        self.layout.add_widget(get_separator('20sp'))
        self.layout.add_widget(self.layout_buttons)

        self.login_button = LoginButton()
        self.login_button.font_name='assets/font.otf'
        # self.layout_buttons.add_widget(self.login_button)

        self.register_button = RegisterButton()
        self.register_button.font_name='assets/font.otf'
        # self.register_button = 
        self.layout_buttons.add_widget(self.register_button)

        self.login_status = LoginStatus()
        self.login_status.font_name='assets/font.otf'
        
        self.layout.add_widget(self.login_status)

        self.label_title.font_size='24sp'
        # self.label_password.font_size='18sp'
        self.label_username.font_size='22sp'
        self.login_button.font_size='12sp'
        self.register_button.font_size='9sp'
        self.register_button.text='enter'
        self.username_field.font_size='24sp'
        self.label_username.padding_x=(10,20)
        self.username_field.padding_x=(20,10)
        # self.username_field.padding_y=(25,0)
        self.username_field.pos_hint={'center_y':0.5}
        self.label_username.halign='right'
        


        ## add all
        self.add_widget(self.layout)
        #pass


    # def on_enter(self):
    #     un=self.app.get_username()
    #     if un: self.username_field.text = un

    def show_pass_opt(self):
        if not self.pass_added:
            self.layout.add_widget(self.layout_password,index=2)
            self.pass_added=True

    def show_pass_opt1(self,button_text='login'):
        if not self.dialog:
            self.dialog = PasswordPopup(
                title="password:",
                type="custom",
                content_cls=MDTextField(password=True),
                buttons=[
                    MDFlatButton(
                        text="login"
                    ),
                ],
            )
        self.dialog.open()

    def getpass_func(self,why_msg,passphrase=None):
        return self.password_field.text if not passphrase else passphrase
        
    async def boot(self,un,pw=None):
        # await self.stat('hello',img_src='/home/ryan/comrad/data/contacts/marxxx.png',comrad_name='Keymaker')

        # await self.app.get_input('hello?',get_pass=True,title='gimme your passwrdd')
        # await self.app.get_input('hello?',get_pass=False,title='gimme your fav color bitch')
        # return
        # self.remove_widget(self.layout)


        # from screens.map import MapWidget,default_places
        # map = MapWidget()
        # map.open()
        # map.add_point(*default_places['Cambridge'],desc='Cambridge')
        # map.draw()
        # await asyncio.sleep(1)
        # map.add_point(*default_places['San Francisco'],desc='San Francisco')
        # map.draw()
        # await asyncio.sleep(1)
        # map.add_point(*default_places['Reykjavik'],desc='Reykjavik')
        # map.draw()
        # await asyncio.sleep(1)
        # return

        # remove login layout for now
        self.remove_widget(self.layout)


        # return
        name=un
        from comrad.backend import Comrad

        
        commie = Comrad(un)
        self.log('KOMMIE!?!?',commie)
        self.log('wtf',PATH_CRYPT_CA_KEYS)

        logger.info(f'booted commie: {commie}')
        if commie.exists_locally_as_account():
            pw='marx' # @HACK FOR NOW
            #pw=await self.app.get_input('Welcome back.',get_pass=True)
            commie.keychain(passphrase=pw)
            logger.info(f'updated keychain: {dict_format(commie.keychain())}')
            logger.info(f'is account')
            # self.login_status.text='You should be able to log into this account.'
            if commie.privkey:
                logger.info(f'passkey login succeeded')
                
                # get new data
                # res = await commie.get_updates()
                # if not res.get('res_login',{}).get('success'):
                #     return {'success':False,'res_refresh':refresh}
                 
                # otherwise, ok
                self.login_status.text=f'Welcome back, Comrad @{un}'
                self.app.is_logged_in=True
                self.app.username=commie.name
                self.app.comrad=commie
                self.root.change_screen('feed')
            else:
                logger.info(f'passkey login failed')
                self.login_status.text='Login failed...'
    

        #   self.layout.add_widget(self.layout_password)
        elif commie.exists_locally_as_contact():
            await self.app.stat('This is a contact of yours')
            self.login_status.text='Comrad exists as a contact of yours.'
            # self.app.change_screen('feed')
            self.app.change_screen('login')
        else:
            # await self.app.stat('Account does not exist on hardware, maybe not on server. Try to register?')
            # self.login_status.text='Comrad not known on this device. Registering...'
            
            ### REGISTER
            self.remove_widget(self.layout)
            res = await self.register(un)
            
            if commie.privkey:
                self.login_status.text='Registered'
                self.app.is_logged_in=True
                self.app.username=commie.name
                self.app.comrad=commie
                self.remove_widget(self.layout)
                self.app.change_screen('feed')
            else:
                self.login_status.text = 'Sign up failed...'
                self.app.change_screen('login')
        return 1

    
    async def register(self,name):
        async def logfunc(*x,**y):
            if not 'comrad_name' in y: y['comrad_name']='Keymaker'
            await self.app.stat(*x,**y)
        
        commie = Comrad(name)
        self.app.comrad = commie

        # already have it?
        if commie.exists_locally_as_account():
            return {'success':False, 'status':'You have already created this account.'}        
        if commie.exists_locally_as_contact():
            return {'success':False, 'status':'This is already a contact of yours'}
            
        # 
        await logfunc(f'Hello, this is Comrad @{name}. I would like to join the socialist network.',pause=True,comrad_name=name)
        
        await logfunc(f'Welcome, Comrad @{name}. To help us communicate safely, I have cut for you a matching pair of encryption keys.',pause=True,clear=True,comrad_name='Keymaker')


        # ## 2) Make pub public/private keys
        from comrad.backend.keymaker import ComradAsymmetricKey
        from comrad.cli.artcode import ART_KEY_PAIR
        keypair = ComradAsymmetricKey()
        logger.info('cut keypair!')
        pubkey,privkey = keypair.pubkey_obj,keypair.privkey_obj
        uri_id = pubkey.data_b64
        uri_s = pubkey.data_b64_s
        fnfn = commie.save_uri_as_qrcode(uri_id=uri_id,name=name)
        
        # await logfunc(f'Here. I have cut for you a private and public asymmetric key pair, using the iron-clad Elliptic curve algorithm:',comrad_name='Keymaker')

        await logfunc(f'The first is your "public key", which you can share with anyone. With it, someone can write you an encrypted message.',comrad_name='Keymaker')
        
        

        # delete qr!
        os.remove(fnfn)

        # await logfunc(f'(1) {pubkey} -- and -- (2) {privkey}',clear=True,pause=True,comrad_name='Keymaker')

        # await logfunc(f'(1) You may store your public key both on your device hardware, as well as share it with anyone you wish: {pubkey.data_b64_s}') #\n\nIt will also be stored as a QR code on your device:\n{qr_str}',pause=True,clear=True)
        


        commie._keychain['pubkey']=pubkey
        commie._keychain['privkey']=privkey
        
        from comrad.utils import dict_format
        self.log('My keychain now looks like:' + dict_format(commie.keychain()))
        # return




        ### PRIVATE KEY
        
        # await logfunc(f"In fact this private encryption is so sensitive we'll encrypt it itself before storing it on your device -- locking the key itself away with a password.",pause=True,use_prefix=False)
        

        # @HACK FOR NOW
        passphrase = 'marx'
        while not passphrase:
            passphrase = await self.app.get_input('Please enter a memorable password.',
                get_pass=True
            )


        passhash = hasher(passphrase)
        privkey_decr = ComradSymmetricKeyWithPassphrase(passhash=passhash)
        print()
        
        # await logfunc(f'''We immediately whatever you typed through a 1-way hashing algorithm (SHA-256), scrambling it into (redacted):\n{make_key_discreet_str(passhash)}''',pause=True,clear=False)

        privkey_encr = privkey_decr.encrypt(privkey.data)
        privkey_encr_obj = ComradEncryptedAsymmetricPrivateKey(privkey_encr)
        commie._keychain['privkey_encr']=privkey_encr_obj
        self.log('My keychain now looks like v2:',dict_format(commie.keychain()))

        # await logfunc(f'With this scrambled password we can encrypt your super-sensitive private key, from this:\n{privkey.discreet}to this:\n{privkey_encr_obj.discreet}',pause=True,clear=False)

        # ### PUBLIC KEY
        await logfunc('You must now register your username and public key with Comrad @Operator on the remote server.',pause=False,clear=False)

        await logfunc('Connecting you to the @Operator...',comrad_name='Telephone')

        ## CALL OP WITH PUBKEY
        # self.app.open_dialog('Calling @Operator...')
        logger.info('got here!')
        resp_msg_d = await self.app.ring_ring(
            {
                'name':name, 
                'pubkey': pubkey.data,
            },
            route='register_new_user',
            commie=commie
        )
        
        # self.app.close_dialog()
        
        
        # print()
        await logfunc(resp_msg_d.get('status'),comrad_name='Operator',pause=True)

        if not resp_msg_d.get('success'):
            self.app.comrad=None
            self.app.is_logged_in=False
            self.app.username=''
            
            # await logfunc('''That's too bad. Cancelling registration for now.''',pause=True,clear=True)
            
            # self.app.change_screen('feed')
            self.app.change_screen('login')
            return

        # clear_screen()
        await logfunc('Great. Comrad @Operator now has your name and public key on file (and nothing else!).',pause=True,clear=True)

        
       

        commie.name=resp_msg_d.get('name')
        pubkey_b = resp_msg_d.get('pubkey')
        assert pubkey_b == pubkey.data
        uri_id = pubkey.data_b64
        sec_login = resp_msg_d.get('secret_login')
        # stop
        
        # await logfunc(f'''Saving keys to device:\n(1) {pubkey}\n(2) {privkey_encr_obj}\n(3) [Shared Login Secret with @Operator]\n({make_key_discreet(sec_login)}''',pause=True)
        # await logfunc(f'''Saving keys to device''',pause=True)

        # print()
        commie.crypt_keys.set(name, pubkey_b, prefix='/pubkey/')
        commie.crypt_keys.set(uri_id, name, prefix='/name/')
        commie.crypt_keys.set(uri_id,sec_login,prefix='/secret_login/')

        # store privkey pieces
        commie.crypt_keys.set(uri_id, privkey_encr_obj.data, prefix='/privkey_encr/')
        # just to show we used a passphrase -->
        commie.crypt_keys.set(uri_id, ComradSymmetricKeyWithPassphrase.__name__, prefix='/privkey_decr/')


        # save qr too:
        _fnfn=commie.save_uri_as_qrcode(uri_id)
        # await logfunc(f'Saving public key, encrypted private key, and login secret to hardware-only database. Also saving public key as QR code to: {_fnfn}.',pause=True,clear=False,use_prefix=False)

        await logfunc(f'You can share it by pasting it to someone in a secure message:\n\n{uri_s}',comrad_name='Keymaker')
        
        await logfunc(f'You can also share it IRL, phone to phone, as a QR code. It is saved to {fnfn} and looks like this.',img_src=fnfn,comrad_name='Keymaker')

        await logfunc(f"(2) Your PRIVATE encryption key, on the other hand, will be stored encrypted on your device hardware. Do not share it with anyone or across any network whatsoever.")
        
        # done!
        await logfunc(f'Congratulations. Welcome, {commie}.',pause=True,clear=True)
        
        # remove all dialogs!!!!!!!!
        # last minute: get posts
        if 'res_posts' in resp_msg_d and resp_msg_d['res_posts'].get('success'):
            id2post=resp_msg_d.get('res_posts').get('posts',{})
            if id2post:
                commie.log('found starter posts:',list(id2post.keys()))
            commie.save_posts(id2post)
            resp_msg_d['status']+=f'  You\'ve got {len(id2post)} new posts and 0 new messages.'
        


        # await logfunc('Returning...')

        from comrad.app.screens.map import MapWidget
        if self.app.map:
            self.app.map.dismiss()
            self.app.map=None
        self.app.change_screen('feed')
        
        return resp_msg_d

    