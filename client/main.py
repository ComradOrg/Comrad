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


class PostCard(MDCard):
    def __init__(self, title = None, img_src = None, content = None):
        super().__init__()
        self.orientation="vertical"
        self.padding="8dp"
        self.size_hint=(0.9, 0.9)
        # self.md_bg_color=(1,0,0,1)
        self.pos_hint = {"center_x": .5, "center_y": .5}
        
        if title:
            sep = MDSeparator()
            sep.height='25dp'
            self.add_widget(sep)

            title = MDLabel(text=title)
            # title.theme_text_color="Secondary"
            title.size_hint_y=None
            title.height=title.texture_size[1]
            title.font_style='H5'
            title.halign='center'
            self.add_widget(title)

            # spacing?
            sep = MDSeparator()
            sep.height='25dp'
            self.add_widget(sep)


        if img_src:
            image = AsyncImage(source=img_src)
            self.add_widget(image)

        if content:
            content=MDLabel(text=content)
            content.pos_hint={'center_y':1}
            content.font_style='Body1'
            self.add_widget(content)


class FeedScreen(MDScreen):
    def on_enter(self):
        i=0
        lim=5
        with open('tweets.txt') as f:
            for ln in f:
                if ln.startswith('@') or ln.startswith('RT '): continue
                i+=1
                if i>lim: break
                
                #post = Post(title=f'Marx Zuckerberg', content=ln.strip())
                post = PostCard(title='Marx Zuckerberg',img_src='avatar.jpg',content=ln.strip())
                print(post)
                root.ids.post_carousel.add_widget(post)
                

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
