from screens.base import BaseScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from main import MyLabel,rgb

class LoginBoxLayout(MDBoxLayout): pass
class LoginButtonLayout(MDBoxLayout): pass
class UsernameField(MDTextField): pass
class PasswordField(MDTextField): pass
class LoginButton(MDRectangleFlatButton): pass
class RegisterButton(MDRectangleFlatButton): pass
class LoginStatus(MDLabel): pass

class UsernameLayout(MDBoxLayout): pass
class UsernameLabel(MDLabel): pass

class LoginScreen(BaseScreen): 
    #def on_pre_enter(self):
    #    global app
    #    if app.is_logged_in():
    #        app.root.change_screen('feed')
    def on_pre_enter(self):
        #log(self.ids)
        #log('hello?')
        self.layout = LoginBoxLayout()

        self.layout_username = UsernameLayout()
        self.label_username = UsernameLabel(text="username:")

        self.username_field = UsernameField()
        self.username_field.line_color_focus=rgb(201,203,163)
        self.username_field.line_color_normal=rgb(201,203,163,0.25)
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
        self.password_field.line_color_focus=rgb(201,203,163)
        self.password_field.line_color_normal=rgb(201,203,163,0.25)
        self.password_field.font_name='assets/font.otf'
        
        self.layout_password.add_widget(self.label_password)
        self.layout_password.add_widget(self.password_field)
        self.layout.add_widget(self.layout_password)

        self.layout_buttons = LoginButtonLayout()
        self.layout.add_widget(self.layout_buttons)

        self.login_button = LoginButton()
        self.login_button.font_name='assets/font.otf'
        self.layout_buttons.add_widget(self.login_button)

        self.register_button = RegisterButton()
        self.register_button.font_name='assets/font.otf'
        # self.register_button = 
        self.layout_buttons.add_widget(self.register_button)

        self.login_status = LoginStatus()
        self.login_status.font_name='assets/font.otf'
        
        self.layout.add_widget(self.login_status)

        self.label_password.font_size='18sp'
        self.label_username.font_size='18sp'


        ## add all
        self.add_widget(self.layout)
        #pass


    def on_enter(self):
        un=self.app.get_username()
        if un: self.username_field.text = un
        