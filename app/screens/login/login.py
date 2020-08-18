from screens.base import BaseScreen
from main import log
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel

class LoginBoxLayout(MDBoxLayout): pass
class LoginButtonLayout(MDBoxLayout): pass
class UsernameField(MDTextField): pass
class PasswordField(MDTextField): pass
class LoginButton(MDRectangleFlatButton): pass
class RegisterButton(MDRectangleFlatButton): pass
class LoginStatus(MDLabel): pass

class LoginScreen(BaseScreen): 
    #def on_pre_enter(self):
    #    global app
    #    if app.is_logged_in():
    #        app.root.change_screen('feed')
    def on_pre_enter(self):
        #log(self.ids)
        #log('hello?')
        self.layout = LoginBoxLayout()
        
        self.username_field = UsernameField()
        self.username_field.line_color_focus=(1,0,0,1)
        self.layout.add_widget(self.username_field)
        #log(self.username_field)
        # self.username_field.text='hello????'

        self.password_field = PasswordField()
        self.password_field.line_color_focus=(1,0,0,1)
        self.layout.add_widget(self.password_field)

        self.layout_buttons = LoginButtonLayout()
        self.layout.add_widget(self.layout_buttons)

        self.login_button = LoginButton()
        self.layout_buttons.add_widget(self.login_button)

        self.register_button = RegisterButton()
        # self.register_button = 
        self.layout_buttons.add_widget(self.register_button)

        self.login_status = LoginStatus()
        self.layout.add_widget(self.login_status)


        ## add all
        self.add_widget(self.layout)
        #pass


    def on_enter(self):
        un=self.app.get_username()
        if un: self.username_field.text = un
        