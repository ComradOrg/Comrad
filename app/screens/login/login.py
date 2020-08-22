from screens.base import BaseScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDSeparator
from kivy.uix.label import Label
from main import MyLabel,rgb,COLOR_TEXT,COLOR_ICON,COLOR_ACCENT,COLOR_CARD
from misc import *
from kivy.app import App

class LoginBoxLayout(MDBoxLayout): pass
class LoginButtonLayout(MDBoxLayout): pass
class UsernameField(MDTextField): pass
class PasswordField(MDTextField): pass
class LoginButton(MDRectangleFlatButton): pass
class RegisterButton(MDRectangleFlatButton):
    def register(self):
        un=self.parent.parent.parent.username_field.text
        app=App.get_running_app()
        app.register(un)
        # app.change_screen_from_uri(f'/inbox/{un}')
    
    pass
class LoginStatus(MDLabel): pass

class UsernameLayout(MDBoxLayout): pass
class UsernameLabel(MDLabel): pass
class WelcomeLabel(MDLabel): pass

class LoginScreen(BaseScreen): 
    #def on_pre_enter(self):
    #    global app
    #    if app.is_logged_in():
    #        app.root.change_screen('feed')
    def on_pre_enter(self):
        #log(self.ids)
        #log('hello?')
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

        # self.login_button = LoginButton()
        # self.login_button.font_name='assets/font.otf'
        # self.layout_buttons.add_widget(self.login_button)

        self.register_button = RegisterButton()
        self.register_button.font_name='assets/font.otf'
        # self.register_button = 
        self.layout_buttons.add_widget(self.register_button)

        self.login_status = LoginStatus()
        self.login_status.font_name='assets/font.otf'
        
        self.layout.add_widget(self.login_status)

        self.label_title.font_size='18sp'
        # self.label_password.font_size='18sp'
        self.label_username.font_size='20sp'
        # self.login_button.font_size='12sp'
        self.register_button.font_size='9sp'
        self.register_button.text='enter'
        self.username_field.font_size='20sp'
        self.label_username.padding_x=(10,20)
        self.username_field.padding_x=(20,10)
        self.username_field.padding_y=(25,0)
        


        ## add all
        self.add_widget(self.layout)
        #pass


    def on_enter(self):
        un=self.app.get_username()
        if un: self.username_field.text = un
        