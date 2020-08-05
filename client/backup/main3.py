from kivy.uix.screenmanager import Screen,ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.theming import ThemeManager
from kivy.properties import ObjectProperty,ListProperty
import time
from collections import OrderedDict
from functools import partial
from kivy.uix.screenmanager import NoTransition
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget
from kivymd.uix.list import OneLineListItem
from kivymd.uix.card import MDCard, MDSeparator
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivymd.uix.list import * #MDList, ILeftBody, IRightBody, ThreeLineAvatarListItem, TwoLineAvatarListItem, BaseListItem, ImageLeftWidget
from kivy.uix.image import Image, AsyncImage

root = None
app = None

def log(x):
    with open('log.txt','a+') as of:
        of.write(str(x)+'\n')

class MyLayout(BoxLayout):
    scr_mngr = ObjectProperty(None)
    def change_screen(self, screen, *args):
        self.scr_mngr.current = screen


class MyLabel(MDLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme_text_color='Custom'
        self.text_color=(1,0,0,1)
        self.pos_hint = {'center_y': 0.5}
        self.halign='center'
        self.height=self.texture_size[1]
        for k,v in kwargs.items(): setattr(self,k,v)

class ContactPhoto(ILeftBody, AsyncImage):
    pass

class Post(TwoLineAvatarListItem):
    """
    text: "Three-line item with avatar"
                        secondary_text: "Secondary text here"
                        tertiary_text: "fit more text than usual"
                        text_color: 1,0,0,1
                        theme_text_color: 'Custom'
    """
    def __init__(self, title, content, *args, **kwargs):
        super().__init__() #*args, **kwargs)
        self.text = title
        self.secondary_text = content
        
        # self.theme_text_color='Custom'
        # self.secondary_theme_text_color = 'Custom'
        
        # self.text_color=(1,0,0,1)
        # self.secondary_text_color = (1,0,0,1)

        avatar = ImageLeftWidget()
        avatar.source = 'avatar.jpg'
        self.add_widget(avatar)

        #icon = ImageRightWidget()
        # icon.icon = 'messages'

        #self.add_widget(icon)

class PostWrapped(BaseListItem):
    """
    text: "Three-line item with avatar"
                        secondary_text: "Secondary text here"
                        tertiary_text: "fit more text than usual"
                        text_color: 1,0,0,1
                        theme_text_color: 'Custom'
    """
    def __init__(self, title, content, *args, **kwargs):
        super().__init__() #*args, **kwargs)
        # self.text = title
        # self.secondary_text = content
        
        # # self.theme_text_color='Custom'
        # # self.secondary_theme_text_color = 'Custom'
        
        # # self.text_color=(1,0,0,1)
        # # self.secondary_text_color = (1,0,0,1)

        # avatar = ImageLeftWidget()
        # avatar.source = 'avatar.jpg'
        # self.add_widget(avatar)
        self.size_hint_y=None
        self.height='100dp'
        avatar = ImageLeftWidget()
        avatar.source = 'avatar.jpg'
        self.add_widget(avatar)
        # self.add_widget(MyLabel(text=title,pos_hint={'center_y': 0.85},halign='left'))
        # self.add_widget(MyLabel(text=content,pos_hint={'center_y': 0.45},halign='left'))
        


class FeedScreen(MDScreen):
    def on_enter(self):
        lim=25
        with open('tweets.txt') as f:
            for i,ln in enumerate(f):
                if i>lim: break
                    
                post = Post(title=f'Marx Zuckerberg', content=ln.strip())
                
                sep = MDSeparator()
                sep.height='1dp'

                root.ids.container.add_widget(post)
                root.ids.container.add_widget(sep)

class WelcomeScreen(MDScreen): pass
class PeopleScreen(MDScreen): pass
class EventsScreen(MDScreen): pass
class MessagesScreen(MDScreen): pass
class NotificationsScreen(MDScreen): pass


 
class MainApp(MDApp):
    title = 'Gyre'

    def build(self):
        global app,root
        app = self
        self.root = root = Builder.load_file('main.kv')
        self.root.change_screen('feed')
        return self.root


if __name__ == '__main__':
    App = MainApp()
    App.run()
