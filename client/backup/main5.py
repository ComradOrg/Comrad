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
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivymd.uix.list import * #MDList, ILeftBody, IRightBody, ThreeLineAvatarListItem, TwoLineAvatarListItem, BaseListItem, ImageLeftWidget
from kivy.uix.image import Image, AsyncImage
import requests,json
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.core.text import LabelBase

Window.size = (640, 1136) #(2.65 * 200, 5.45 * 200)


root = None
app = None

def log(x):
    with open('log.txt','a+') as of:
        of.write(str(x)+'\n')

class MyLayout(MDBoxLayout):
    scr_mngr = ObjectProperty(None)

    def change_screen(self, screen, *args):
        self.scr_mngr.current = screen


class MyBoxLayout(MDBoxLayout): pass
class MyLabel(MDLabel): pass


### POST CODE
class PostTitle(MDLabel): pass
class PostGridLayout(GridLayout): pass
class PostImage(AsyncImage): pass

class PostContent(MDLabel): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.bind(texture_size=self.setter('size'))
        self.font_name='assets/overpass-mono-regular.otf'
    #pass

class PostAuthorLayout(MDBoxLayout): pass

class PostAuthorLabel(MDLabel): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.bind(texture_size=self.setter('size'))
        self.font_name='assets/overpass-mono-regular.otf'
    pass
class PostAuthorAvatar(AsyncImage): pass

class PostCard(MDCard):
    def __init__(self, author = None, title = None, img_src = None, content = None):
        super().__init__()
        self.author = author
        self.title = title
        self.img_src = img_src
        self.content = content
        self.bind(minimum_height=self.setter('height'))

        # pieces
        author_section_layout = PostAuthorLayout()
        author_label = PostAuthorLabel(text=self.author)
        author_label.font_size = '28dp'
        author_avatar = PostAuthorAvatar(source=self.img_src)
        author_section_layout.add_widget(author_avatar)
        author_section_layout.add_widget(author_label)
        # author_section_layout.add_widget(author_avatar)
        self.add_widget(author_section_layout)

        
        title = PostTitle(text=self.title)
        # image = PostImage(source=self.img_src)
        content = PostContent(text=self.content)
        
        #content = PostContent()

        # add to screen
        self.add_widget(title)
        # self.add_widget(image)
        self.add_widget(content)
        #self.add_widget(layout)

#####



#### LOGIN

class ProtectedScreen(MDScreen):
    def on_pre_enter(self):
        global app
        if not app.is_logged_in():
            app.root.change_screen('login')
        



class WelcomeScreen(ProtectedScreen): pass
class LoginScreen(MDScreen): 
    #def on_pre_enter(self):
    #    global app
    #    if app.is_logged_in():
    #        app.root.change_screen('feed')
    pass
    
class PeopleScreen(ProtectedScreen): pass
class AddPostScreen(ProtectedScreen): pass
class EventsScreen(ProtectedScreen): pass
class MessagesScreen(ProtectedScreen): pass
class NotificationsScreen(ProtectedScreen): pass


class FeedScreen(ProtectedScreen):
    def on_enter(self):
        i=0
        lim=5
        with open('tweets.txt') as f:
            for ln in f:
                if ln.startswith('@') or ln.startswith('RT '): continue
                i+=1
                if i>lim: break
                
                #post = Post(title=f'Marx Zuckerberg', content=ln.strip())
                post = PostCard(
                    author='Marx Zuckerberg',
                    title='',
                    img_src='avatar.jpg',
                    content=ln.strip())
                print(post)
                root.ids.post_carousel.add_widget(post)

                
        



def get_tor_proxy_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session    

def get_tor_python_session():
    from torpy.http.requests import TorRequests
    with TorRequests() as tor_requests:
        with tor_requests.get_session() as s:
            return s

from kivymd.font_definitions import theme_font_styles
class MainApp(MDApp):
    title = 'Komrade'
    #api = 'http://localhost:5555/api'
    api = 'http://128.232.229.63:5555/api'
    #api = 'http://komrades.net:5555/api'
    logged_in=False
    store = JsonStore('komrade.json')
    login_expiry = 60 * 60 * 24 * 7  # once a week
    #login_expiry = 5 # 5 seconds

    def get_session(self):
        return get_tor_proxy_session()
        #return get_tor_python_session()

    def build(self):
        # bind 
        global app,root
        app = self
        self.root = root = Builder.load_file('main.kv')
        
        # edit logo
        logo=root.ids.toolbar.ids.label_title
        logo.font_name='assets/Strengthen.ttf'
        logo.font_size='58dp'
        logo.pos_hint={'center_y':0.43}
        # icons
        icons=root.ids.toolbar.ids.right_actions.children
        for icon in icons:
            #log(dir(icon))
            #icon.icon='android' #user_font_size='200sp'
            icon.font_size='58dp'
            icon.user_font_size='58dp'
            icon.width='58dp'
            icon.size_hint=(None,None)
            icon.height='58dp'
 
        if not self.is_logged_in():
            self.root.change_screen('login')
        else:
            self.root.change_screen('feed')
        return self.root

    def is_logged_in(self):
        if self.logged_in: return True
        if not self.store.exists('user'): return False
        if self.store.get('user')['logged_in']:
            if time.time() - self.store.get('user')['logged_in_when'] < self.login_expiry:
                self.logged_in=True
                return True
        return False

    def do_login(self):
        self.logged_in=True
        self.store.put('user',logged_in=True,logged_in_when=time.time())
        self.root.change_screen('feed')


    def login(self,un,pw):
        url = self.api+'/login'

        with self.get_session() as sess:
            #res = requests.post(url, json={'name':un, 'passkey':pw})
            res = sess.post(url, json={'name':un, 'passkey':pw})

            if res.status_code==200:
                self.do_login()
            else:
                self.root.ids.login_status.text=res.text

    def register(self,un,pw):
        url = self.api+'/register'

        with self.get_session() as sess:
            #res = requests.post(url, json={'name':un, 'passkey':pw})
            res = sess.post(url, json={'name':un, 'passkey':pw})
            if res.status_code==200:
                self.do_login()
            else:
                self.root.ids.login_status.text=res.text




if __name__ == '__main__':
    App = MainApp()
    App.run()
