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
    kwargs = dict(
                    theme_text_color='Custom',
                    text_color=(1,0,0,1), 
                    pos_hint = {'center_y': 0.5},
                    halign='center')
    def __init__(self, *args, **kwargs):
        kwargs = dict(list(self.kwargs.items()) + list(kwargs.items()))
        super().__init__(*args, **kwargs) 

class Post(MDCard):
    """MDCard:
        orientation: "vertical"
        padding: "8dp"
        size_hint: None, None
        size: "280dp", "180dp"
        pos_hint: {"center_x": .5, "center_y": .5}

        MDLabel:
            text: "Title"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: self.texture_size[1]

        MDSeparator:
            height: "1dp"

        MDLabel:
            text: "Body"
    """

    def __init__(self, title, content):
        super().__init__()
        self.orientation='vertical'
        # self.padding='8dp'
        # self.size_hint = (None, None)
        # self.size = ("280dp", "50dp")
        self.pos_hint = {"center_x": .5, "center_y": .5}
        self.md_bg_color = (0,0,0,1)
        self.halign = 'center'

        self.add_widget(MyLabel(text=title))
        # self.add_widget(MDSeparator(height='1dp'))
        self.add_widget(MyLabel(text=content))


class FeedScreen(MDScreen):
    def on_enter(self):
        for i in range(20):
            root.ids.container.add_widget(
                Post(title=f'Post {i}', content='This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content This is the content ')
            )

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
        return self.root


if __name__ == '__main__':
    App = MainApp()
    App.run()
