## CONFIG
# change this to your external ip address for your server
#(needs to be external to allow tor routing)
DEFAULT_SCREEN='profile'

import random
HORIZONTAL = False #random.choice([True,True,True,False])
FACTOR=1
WINDOW_SIZE = (1136*FACTOR,640*FACTOR) if HORIZONTAL else (640*FACTOR,1136*FACTOR)

BG_IMG='assets/bg-russiangreen.png'

grass=(201,203,163)
russiangreen = (109,140,96)
huntergreen = (67,92,61)
kombugreen = (49,67,45)
pinetreegreen = (29,40,27)
junglegreen = (15, 21, 14)

browncoffee=(77, 42, 34)
rootbeer=(38, 7, 1)
blackbean=(61, 12, 2)
burntumber=(132, 55, 34)
brownsugar=(175, 110, 81)
antiquebrass= (198, 144, 118)
royalbrown=(94, 55, 46)
bole=(113, 65, 55)
liver= (110, 56, 31)
bistre=(58, 33, 14)
skin1=(89, 47, 42)
skin2=(80, 51, 53)
skin3=(40, 24, 26)

grullo=177, 158, 141
smokyblack=33, 14, 0
liverchestnut=148, 120, 96
ashgray=196, 199, 188
livchestnut2=156, 106, 73
beaver=165, 134, 110
rawumber=120, 95, 74

dutchwhite=229,219,181

COLOR_TOOLBAR= smokyblack #5,5,5 #russiangreen #pinetreegreen #kombugreen #(12,5,5) #russiangreen
COLOR_BG = (0,73,54)
# COLOR_ICON = (201,203,163)
COLOR_LOGO = grullo#russiangreen #(0,0,0) #(0,0,0) #(151,177,140) #(132,162,118) #(109,140,106)
COLOR_ICON = grullo#russiangreen #(0,0,0) #COLOR_LOGO
COLOR_TEXT =dutchwhite #(241,233,203) #COLOR_ICON #(207,219,204) #(239,235,206) # (194,211,187) # (171,189,163) # (222,224,198) # COLOR_LOGO #(223, 223, 212)
COLOR_CARD = smokyblack #skin2 #huntergreen #(30,23,20) #(51,73,45) # (67,92,61) #(12,9,10)
# COLOR_TOOLBAR = (8s9,59,43)
# COLOR_ICON = COLOR_LOGO = COLOR_TEXT
# COLOR_TEXT=tuple([x+50 for x in russiangreen]) #COLOR_TOOLBAR
# COLOR_ICON = COLOR_LOGO = grass
# COLOR_LOGO = junglegreen #(199,22,22)
# COLOR_ICON = COLOR_LOGO
COLOR_CARD_BORDER = rawumber

# monkeypatching the things that asyncio needs
import subprocess
subprocess.PIPE = -1  # noqa
subprocess.STDOUT = -2  # noqa
subprocess.DEVNULL = -3  # noqa


import asyncio
import os
os.environ['KIVY_EVENTLOOP'] = 'asyncio'
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
def rgb(r,g,b,a=1):
    return (r/255,g/255,b/255,a)

class MyLayout(MDBoxLayout):
    scr_mngr = ObjectProperty(None)
    post_id = ObjectProperty()

    def rgb(self,r,g,b,a=1):
        return rgb(r,g,b,a=a)

    def change_screen(self, screen, *args):
        self.scr_mngr.current = screen
    
    def view_post(self,post_id):
        self.post_id=post_id
        self.change_screen('view')


class MyBoxLayout(MDBoxLayout): pass
class MyLabel(MDLabel): pass

class MyToolbar(MDToolbar):
    action_icon_color = ListProperty()

    def update_action_bar(self, action_bar, action_bar_items):
        action_bar.clear_widgets()
        new_width = 0
        for item in action_bar_items:
            new_width += dp(48)
            action_bar.add_widget(
                MDIconButton(
                    icon=item[0],
                    on_release=item[1],
                    opposite_colors=True,
                    text_color=(self.specific_text_color if not self.action_icon_color else self.action_icon_color),
                    theme_text_color="Custom",
                )
            )
        action_bar.width = new_width

    def update_action_bar_text_colors(self, instance, value):
        for child in self.ids["left_actions"].children:
            if not self.action_icon_color:
                child.text_color = self.specific_text_color
            else:
                child.text_color = self.action_icon_color

        for child in self.ids["right_actions"].children:
            if not self.action_icon_color:
                child.text_color = self.specific_text_color
            else:
                child.text_color = self.action_icon_color




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
    store = JsonStore('../p2p/.keys.json')
    login_expiry = 60 * 60 * 24 * 7  # once a week
    texture = ObjectProperty()

    # def connect(self):
    #     # connect to kad?   
    #     self.node = p2p.connect()
    def rgb(self,*_): return rgb(*_)

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
        toolbar=root.ids.toolbar
        toolbar.md_bg_color = root.rgb(*COLOR_TOOLBAR)
        toolbar.action_icon_color=root.rgb(*COLOR_ICON)
        logo=toolbar.ids.label_title
        logo.font_name='assets/Strengthen.ttf'
        logo.font_size='58dp'
        logo.pos_hint={'center_y':0.43}
        logo.text_color=root.rgb(*COLOR_LOGO)
        
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
        async def do():
            dat = await self.api.login(un,pw)
            self.log(dat)
            if 'success' in dat:
                self.save_login(un)
            elif 'error' in dat:
                self.root.ids.login_screen.login_status.text=dat['error']
            return False
        asyncio.create_task(do())

    def register(self,un,pw):
        async def do():
            dat = await self.api.register(un,pw)
            if 'success' in dat:
                self.save_login(un)
                return True
            elif 'error' in dat:
                self.root.ids.login_screen.login_status.text=dat['error']
                return False
        asyncio.create_task(do())

    async def upload(self,filename,file_id=None):
        self.log('uploading filename:',filename)
        rdata=await self.api.upload(filename,file_id=file_id)
        self.log('upload result:',rdata)
        if rdata is not None:
            rdata['success']='File uploaded'
            return rdata
        return {'error':'Upload failed'}
        
    async def download(self,file_id,output_fn=None):
        self.log('downloading:',file_id)
        file_dat = await self.api.download(file_id)
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
    
    async def post(self, content='', file_id=None, file_ext=None, anonymous=False):
        #timestamp=time.time()
        jsond={}
        #jsond['timestamp']=
        if content: jsond['content']=str(content)
        if file_id: jsond['file_id']=str(file_id)
        if file_ext: jsond['file_ext']=str(file_ext)
        if not anonymous and self.username:
            jsond['author']=self.username
        
        self.log('posting:',jsond)
        res=await self.api.post(jsond)
        if 'success' in res:
            self.root.change_screen('feed')
            return {'post_id':res['post_id']}
                    

                    
            

    async def get_post(self,post_id):
        return await self.api.get_post(post_id)

    async def get_posts(self):
        return await self.api.get_posts()

    async def get_my_posts(self):
        return await self.api.get_posts('/author/'+self.username)



    ### SYNCHRONOUS?
    def app_func(self):
        '''This will run both methods asynchronously and then block until they
        are finished
        '''
        # self.other_task = asyncio.ensure_future(self.waste_time_freely())
        self.other_task = asyncio.ensure_future(self.api.connect_forever())

        async def run_wrapper():
            # we don't actually need to set asyncio as the lib because it is
            # the default, but it doesn't hurt to be explicit
            await self.async_run() #async_lib='asyncio')
            print('App done')
            self.other_task.cancel()

        return asyncio.gather(run_wrapper(), self.other_task)



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MainApp().app_func())
    loop.close()




# def main():
#     # start_logger()
#     App = MainApp()
#     App.run()


# if __name__ == '__main__':
#     # loop = asyncio.get_event_loop()
#     # asyncio.set_event_loop(loop)
#     # loop.run_until_complete(main())
#     # loop.close()
#     main()
