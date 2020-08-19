## CONFIG
# change this to your external ip address for your server
#(needs to be external to allow tor routing)
DEFAULT_SCREEN='feed'
HORIZONTAL = False
WINDOW_SIZE = (1136,640) if HORIZONTAL else (640,1136)

# monkeypatching the things that asyncio needs
import subprocess
subprocess.PIPE = -1  # noqa
subprocess.STDOUT = -2  # noqa
subprocess.DEVNULL = -3  # noqa


import asyncio
import os
os.environ['KIVY_EVENTLOOP'] = 'async'
# loop = asyncio.get_event_loop()
# loop.set_debug(True)

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
import shutil,sys
from kivy.uix.image import Image
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from p2p import p2p,crypto,api
from kivy.event import EventDispatcher
import threading,asyncio,sys


Window.size = WINDOW_SIZE

# with open('log.txt','w') as of:
#     of.write('### LOG ###\n')


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








#### LOOPER








class MainApp(MDApp):
    title = 'Komrade'
    logged_in=False
    store = JsonStore('komrade.json')
    login_expiry = 60 * 60 * 24 * 7  # once a week
    texture = ObjectProperty()

    # def connect(self):
    #     # connect to kad?   
    #     self.node = p2p.connect()
    @property
    def logger(self):
        if not hasattr(self,'_logger'):
            import logging
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self._logger = logger = logging.getLogger(self.title)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
        return self._logger

    def log(self,*args):
        line = ' '.join(str(x) for x in args)
        self.logger.debug(line)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # start looping

        # self.log('PATH',sys.path)
        # sys.path.append('./p2p')



        self.event_loop_worker = None
        self.loop=asyncio.get_event_loop()
        
        # load json storage
        self.username=''
        self.load_store()
        
        # connect to API
        self.api = api.Api(app=self)



    


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
        # bind 
        global app,root
        app = self
        
        # load root
        self.root = root = Builder.load_file('root.kv')
        draw_background(self.root)
        
        # edit logo
        logo=root.ids.toolbar.ids.label_title
        logo.font_name='assets/Strengthen.ttf'
        logo.font_size='58dp'
        logo.pos_hint={'center_y':0.43}
        
        # logged in?
        if not self.is_logged_in():
            self.root.change_screen('login')
        else:
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
        self.log(dat)
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
        self.log('uploading filename:',filename)
        rdata=self.api.upload(filename,file_id=file_id)
        self.log('upload result:',rdata)
        if rdata is not None:
            rdata['success']='File uploaded'
            return rdata
        return {'error':'Upload failed'}
        
    def download(self,file_id,output_fn=None):
        self.log('downloading:',file_id)
        file_dat = self.api.download(file_id)
        if not output_fn:
            file_id=file_dat['id']
            file_ext=file_dat['ext']
            output_fn=os.path.join('cache',file_id[:3]+'/'+file_id[3:]+'.'+file_ext)
        
        output_dir=os.path.dirname(output_fn)
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        with open(output_fn,'wb') as of:
            for data_piece in file_dat['parts_data']:
                if data_piece is not None:
                    of.write(data_piece)
    
    def post(self, content='', file_id=None, file_ext=None, anonymous=False):
        #timestamp=time.time()
        jsond={}
        #jsond['timestamp']=
        if content: jsond['content']=str(content)
        if file_id: jsond['file_id']=str(file_id)
        if file_ext: jsond['file_ext']=str(file_ext)
        if not anonymous and self.username:
            jsond['author']=self.username
        
        self.log('posting:',jsond)
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
            self.log('getting image!')
            with self.get_session() as sess:
                with sess.get(self.api+'/download/'+img_src,stream=True) as r:
                    with open(ofn_image,'wb') as of:
                        shutil.copyfileobj(r.raw, of)
        return ofn_image




def main():
    # start_logger()
    App = MainApp()
    App.run()


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(main())
    # loop.close()
    main()
