from kivy.uix.screenmanager import Screen,ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.theming import ThemeManager
from kivy.properties import ObjectProperty,ListProperty
import time,os
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

def log(x):
    with open('log.txt','a+') as of:
        of.write(str(x)+'\n')



class MyLayout(MDBoxLayout):
    scr_mngr = ObjectProperty(None)
    post_id = ObjectProperty()

    def change_screen(self, screen, *args):
        self.scr_mngr.current = screen
    
    def view_post(self,post_id):
        self.post_id=post_id
        self.change_screen('view')


class MyBoxLayout(MDBoxLayout): pass
class MyLabel(MDLabel): pass




#### LOGIN





                
        



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
            self.root.change_screen('post')
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

    def post(self, content='', img_src=[]):
        log('content: '+str(content))
        log('img_src: '+str(img_src))

        jsond = {'content':str(content)}

        # upload?
        filename=img_src[0] if img_src and os.path.exists(img_src[0]) else ''            
        
        url_upload=self.api+'/upload'
        url_post = self.api+'/post'
        
        server_filename=''
            
        if filename:
            with self.get_session() as sess:
            #res = sess.post(url, files=filesd, data={'data':json.dumps(jsond)}, headers=headers)
                log(filename)
                self.root.ids.add_post_screen.ids.post_status.text='Uploading file'
                r = sess.post(url_upload,files={'file':open(filename,'rb')})
                if r.status_code==200:
                    server_filename = r.text
                    self.root.ids.add_post_screen.ids.post_status.text='File uploaded'
            
        with self.get_session() as sess:
            # add post
            #log(self.root.ids.add_post_screen.ids.keys())
            self.root.ids.add_post_screen.ids.post_status.text='Creating post'
            jsond={'img_src':server_filename, 'content':content}
            r = sess.post(url_post, json=jsond)
            log('got back from post: ' + r.text)
            post_id = r.text
            if post_id.isdigit():
                self.root.ids.add_post_screen.ids.post_status.text='Post created'
                self.root.view_post(int(post_id))

        def get_post(self,post_id):
            with self.get_session() as sess:
                r = sess.get(self.api+'/post/'+str(post_id))
                print(r.text)


if __name__ == '__main__':
    App = MainApp()
    App.run()
