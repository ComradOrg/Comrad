import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
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
        login_screen = self.parent.parent.parent

        login_screen.boot(un)

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
        # self.label_title.font_size*=1.5
        self.layout.add_widget(get_separator('20sp'))
        self.layout.add_widget(self.label_title)
        self.layout.add_widget(get_separator('30sp'))
        # self.layout.add_widget(MySeparator())
        

        self.layout_username = UsernameLayout()
        self.label_username = UsernameLabel(text="Komrade")

        self.username_field = UsernameField()
        self.username_field.line_color_focus=rgb(*COLOR_TEXT)
        self.username_field.line_color_normal=rgb(*COLOR_TEXT,a=0.25)
        self.username_field.font_name='assets/font.otf'

        self.layout_username.add_widget(self.label_username)
        self.layout_username.add_widget(self.username_field)

        self.layout.add_widget(self.layout_username)
        #log(self.username_field)
        # self.username_field.text='hello????'

        self.layout_password = UsernameLayout()
        self.label_password = UsernameLabel(text='password:')

        self.label_password.font_name='assets/font.otf'
        self.label_username.font_name='assets/font.otf'

        self.password_field = PasswordField()
        self.password_field.line_color_focus=rgb(*COLOR_TEXT)
        self.password_field.line_color_normal=rgb(*COLOR_TEXT,a=0.25)
        self.password_field.font_name='assets/font.otf'
        
        self.layout_password.add_widget(self.label_password)
        self.layout_password.add_widget(self.password_field)
        self.layout.add_widget(self.layout_password)

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

        self.label_title.font_size='18sp'
        self.label_password.font_size='18sp'
        self.label_username.font_size='20sp'
        self.login_button.font_size='12sp'
        self.register_button.font_size='9sp'
        self.register_button.text='enter'
        self.username_field.font_size='20sp'
        self.label_username.padding_x=(10,20)
        self.username_field.padding_x=(20,10)
        self.username_field.padding_y=(25,0)
        


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

    def getpass_func(self,why_msg):
        return self.password_field.text
        
    def boot(self,un):

        # self.app.stat(
        #     'You chose the username '+un
        # )


        # return
        kommie = Komrade(un,getpass_func=self.getpass_func)
        # self.show_pass_opt()
        logger.info(f'booted kommie: {kommie}')
        if kommie.exists_locally_as_account():
            logger.info(f'is account')
            self.login_status.text='You should be able to log into this account.'
            if kommie.privkey:
                logger.info(f'passkey login succeeded')
                self.login_status.text=f'Welcome back, Komrade @{un}'
                self.app.is_logged_in=True
                self.app.username=kommie.name
                self.app.komrade=kommie
                self.remove_widget(self.layout)
                self.root.change_screen('feed')
            else:
                logger.info(f'passkey login failed')
                self.login_status.text='Login failed...'

        #   self.layout.add_widget(self.layout_password)
        elif kommie.exists_locally_as_contact():
          self.login_status.text='Komrade exists as a contact of yours.'
        else:
            self.login_status.text='Komrade not known on this device. Registering...'
            res = kommie.register(logfunc=self.app.stat)
            if kommie.privkey:
                self.login_status.text='Registered'
                self.app.is_logged_in=True
                self.app.username=kommie.name
                self.app.komrade=kommie
                self.remove_widget(self.layout)
                self.app.change_screen('feed')
            else:
                self.login_status.text = 'Sign up failed...'