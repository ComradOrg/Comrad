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
from kivymd.uix.list import MDList, ThreeLineAvatarListItem


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


class ScrollCenterLayout(GridLayout):
    rel_max = NumericProperty(dp(800))
    rel_min = NumericProperty(dp(400))

    def __init__(self, **kwargs):
        super(ScrollCenterLayout, self).__init__(**kwargs)

        self.rel_max = kwargs.get('rel_max', dp(800))
        self.rel_min = kwargs.get('rel_min', dp(400))

    def on_width(self, instance, value):
        if self.rel_max < value:
            padding = max(value * .125, (value - self.rel_max) / 2)
        elif self.rel_min < value:
            padding = min(value * .125, (value - self.rel_min) / 2)
        elif self.rel_min < value:
            padding = (value - self.rel_min) / 2
        else:
            padding = 0

        self.padding[0] = self.padding[2] = padding


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

    def __init__(self, title, author, content):
        super().__init__()
        self.orientation='vertical'
        self.padding=dp(15)
        self.size_hint = (1, None)
        self.pos_hint = {"center_x": .5, "center_y": .5}
        self.md_bg_color = (0.1,0.1,0.1,1)
        self.halign = 'center'
        self.add_widget(MyLabel(text=title, halign='left', size_hint_y=None)) #, size_hint_y=None, height='10dp'))
        # self.add_widget(MyLabel(text=author, halign='left')) #, size_hint_y=None, height='10dp'))
        self.add_widget(MyLabel(text=content, halign='left')) #, size_hint_y=None, height='50dp'))
        

class FeedScreen(MDScreen):
    def on_enter(self):
        for i in range(25):
            post = Post(title=f'Title {i}', author=f'Author {i}', content='This is the content')
            
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
