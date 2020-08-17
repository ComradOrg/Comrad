## CONFIG
# change this to your external ip address for your server
#(needs to be external to allow tor routing)
SERVER_ADDR = '128.232.229.63:5555'
DEFAULT_SCREEN='profile'
HORIZONTAL = False
WINDOW_SIZE = (1136,640) if HORIZONTAL else (640,1136)

# imports
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
import shutil
from kivy.uix.image import Image
from p2p import p2p,crypto,api

Window.size = WINDOW_SIZE

# with open('log.txt','w') as of:
#     of.write('### LOG ###\n')

import logging
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger('app')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def log(*args):
    #with open('log.txt','a+') as of:
    #    of.write(' '.join([str(x) for x in args])+'\n')
    line = ' '.join(str(x) for x in args)
    logger.debug(line)

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





def get_tor_proxy_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9150',
                       'https': 'socks5://127.0.0.1:9150'}
    return session    

def get_async_tor_proxy_session():
    from requests_futures.sessions import FuturesSession
    session = FuturesSession()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9150',
                       'https': 'socks5://127.0.0.1:9150'}
    return session    


def get_tor_python_session():
    from torpy.http.requests import TorRequests
    with TorRequests() as tor_requests:
        with tor_requests.get_session() as s:
            return s

def draw_background(widget, img_fn='assets/bg.png'):
    from kivy.core.image import Image as CoreImage
    from kivy.graphics import Color, Rectangle 
    widget.canvas.before.clear()
    with widget.canvas.before:
        Color(.4, .4, .4, 1)
        texture = CoreImage(img_fn).texture
        texture.wrap = 'repeat'
        nx = float(widget.width) / texture.width
        ny = float(widget.height) / texture.height
        Rectangle(pos=widget.pos, size=widget.size, texture=texture,
                  tex_coords=(0, 0, nx, 0, nx, ny, 0, ny))


class MainApp(MDApp):
    title = 'Komrade'
    logged_in=False
    store = JsonStore('komrade.json')
    login_expiry = 60 * 60 * 24 * 7  # once a week
    texture = ObjectProperty()

    # def connect(self):
    #     # connect to kad?   
    #     self.node = p2p.connect()


    def get_session(self):
        # return get_async_tor_proxy_session()
        return get_tor_proxy_session()
        #return get_tor_python_session()

    def get_username(self):
        if hasattr(self,'username'): return self.username
        self.load_store()
        if hasattr(self,'username'): return self.username
        return ''

    def build(self):
        # bind bg texture
        # self.texture = Image(source='assets/bg.png').texture
        # self.texture.wrap = 'clamp_to_edge'
        # self.texture.uvsize = (-2, -2)

        with open('log.txt','w') as of: of.write('## LOG ##\n')
        self.load_store()

        # self.boot_kad()
        from p2p.api import Api
        self.api = Api(app_storage=self.store)

        self.username=''
        # bind 
        global app,root
        app = self
        #self.username = self.store.get('userd').get('username')
        
        self.root = root = Builder.load_file('root.kv')
        draw_background(self.root)
        
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
            #log(self.username)
        else:
            # self.root.post_id=190
            self.root.change_screen(DEFAULT_SCREEN)
        return self.root

    def load_store(self):
        if not self.store.exists('user'): return
        userd=self.store.get('user')
        if not userd: userd={}
        self.logged_in_when = userd.get('logged_in_when')
        self.username = userd.get('username','')
        
    def is_logged_in(self,just_check_timestamp=True, use_caching=True):
        # self.username='root'
        # return True
        if self.logged_in: return True
        if not use_caching: return False

        ###
        if not self.store.exists('user'): return False
        userd=self.store.get('user')
        if not userd: userd={}
        if userd.get('logged_in'):
            un=userd.get('username')
            timestamp=userd.get('logged_in_when')

            # just a time check
            if timestamp and just_check_timestamp:
                if time.time() - timestamp < self.login_expiry:
                    self.logged_in=True
                    #self.username=un
                    return True
            
        return False

    def save_login(self,un):
        self.logged_in=True
        self.username=un
        # self.store.put('username',un)
        # self.store.put('user',username=un,logged_in=True,logged_in_when=time.time())
        self.root.change_screen('feed')


    def login(self,un=None,pw=None):
        dat = self.api.login(un,pw)
        log(dat)
        if 'success' in dat:
            self.save_login(un)
        elif 'error' in dat:
            self.root.ids.login_screen.login_status.text=dat['error']
        return False

    def register(self,un,pw):
        dat = self.api.register(un,pw)
        if 'success' in dat:
            self.save_login(un)
            return True
        elif 'error' in dat:
            self.root.ids.login_screen.login_status.text=dat['error']
            return False

    def upload(self,filename,file_id=None):
        log('uploading filename:',filename)
        rdata=self.api.upload(filename,file_id=file_id)
        if rdata is not None:
            rdata['success']='File uploaded'
            return rdata
        return {'error':'Upload failed'}
        
        
    
    def post(self, content='', media_uid=None):
        timestamp=time.time()
        jsond = {'content':str(content),'media_uid':media_uid,
                 'author':self.username, 'timestamp':timestamp}
            
        res=self.api.post(jsond)
        if 'success' in res:
            self.root.change_screen('feed')
            return {'post_id':res['post_id']}
                    

                    
            

    def get_post(self,post_id):
        return self.api.get_post(post_id)

    def get_posts(self):
        return self.api.get_posts()

    def get_my_posts(self):
        return self.api.get_posts('/author/'+self.username)


    def get_image(self, img_src):
        # is there an image?
        if not img_src: return 
        # is it cached?
        ofn_image = os.path.join('cache','img',img_src)
        if not os.path.exists(ofn_image):
            # create dir?
            ofn_image_dir = os.path.split(ofn_image)[0]
            if not os.path.exists(ofn_image_dir): os.makedirs(ofn_image_dir)
            log('getting image!')
            with self.get_session() as sess:
                with sess.get(self.api+'/download/'+img_src,stream=True) as r:
                    with open(ofn_image,'wb') as of:
                        shutil.copyfileobj(r.raw, of)
        return ofn_image



if __name__ == '__main__':

    #### LOGIN



    App = MainApp()
    App.run()
