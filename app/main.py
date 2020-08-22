## CONFIG
# change this to your external ip address for your server
#(needs to be external to allow tor routing)
from config import *


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

# raise Exception(str(Window.size))
Window.size = WINDOW_SIZE
# Window.fullscreen = True #'auto'

# with open('log.txt','w') as of:
#     of.write('### LOG ###\n')
def rgb(r,g,b,a=1):
    return (r/255,g/255,b/255,a)

class MyLayout(MDBoxLayout):
    scr_mngr = ObjectProperty(None)
    post_id = ObjectProperty()

    @property
    def app(self):
        if not hasattr(self,'_app'):
            from kivy.app import App
            self._app = App.get_running_app()
        return self._app

    def rgb(self,r,g,b,a=1):
        return rgb(r,g,b,a=a)

    def change_screen(self, screen, *args):
        self.scr_mngr.current = screen

    def change_screen_from_uri(self,uri,*args):
        screen_name = route(uri)
        self.app.screen = screen_name
        self.app.log(f'routing to {screen_name}')
        self.scr_mngr.current = screen_name
    
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



def route(uri):
    if not '/' in uri: return None
    prefix=uri.split('/')[1] #,channel,rest = uri.split('/',3)

    mapd = {
        'inbox':'feed',
        'outbox':'feed',
        'login':'login',
    }
    return mapd.get(prefix,None)



# DEFAULT_SCREEN = route(DEFAULT_URI)

class MainApp(MDApp):
    title = 'Komrade'
    logged_in=False
    store = JsonStore('../p2p/.keys.json')
    store_global = JsonStore('../p2p/.keys.global.json')
    login_expiry = 60 * 60 * 24 * 7  # once a week
    texture = ObjectProperty()

    # def connect(self):
    #     # connect to kad?   
    #     self.node = p2p.connect()
    def rgb(self,*_): return rgb(*_)

    def change_screen(self, screen, *args):
        self.screen=screen
        self.root.change_screen(screen,*args)

    def change_screen_from_uri(self,uri,*args):
        self.uri=uri
        self.log('CHANGING SCREEN',uri,'??')
        return self.root.change_screen_from_uri(uri,*args)

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
        self.event_loop_worker = None
        self.loop=asyncio.get_event_loop()
        
        # load json storage
        self.username=''
        self.load_store()
        self.uri=DEFAULT_URI
        # connect to API
        self.api = api.Api(log=self.log)

    @property
    def channel(self):
        return self.uri.split('/')[1] if self.uri and self.uri.count('/')>=2 else None
        

    


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
        
        self.root.change_screen_from_uri(self.uri if self.uri else DEFAULT_URI)
        
        return self.root




    def load_store(self):
        if not self.store.exists('user'): return
        userd=self.store.get('user')
        if not userd: return

        self.username = userd.get('username','')
    
    def register(self,un):
        async def do():
            dat = await self.api.register(un)
            if 'success' in dat:
                self.username=un
                self.store.put('user',username=un)
                self.root.ids.login_screen.login_status.text=dat['success']
                self.root.ids.login_screen.login_status.theme_text_color='Custom'
                self.root.ids.login_screen.login_status.text_color=rgb(*COLOR_ACCENT)
                await asyncio.sleep(1)
                #self.save_login(dat)
                self.change_screen_from_uri('/inbox/world')
                return True
            elif 'error' in dat:
                self.root.ids.login_screen.login_status.text=dat['error']
                # await asyncio.sleep(3)
                # self.change_screen_from_uri('/inbox/world')
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
        self.log('file_dat =',file_dat)
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
    
    async def post(self, content='', file_id=None, file_ext=None, anonymous=False,channels=['world']):
        #timestamp=time.time()
        jsond={}
        #jsond['timestamp']=
        if content: jsond['content']=str(content)
        if file_id: jsond['file_id']=str(file_id)
        if file_ext: jsond['file_ext']=str(file_ext)
        self.log(f'''app.json(
            content={content},
            file_id={file_id},
            file_ext={file_ext},
            anonymous={anonymous},
            channels={channels},
            [username={self.username}]'''
        )
        if not anonymous and self.username:
            jsond['author']=self.username
        jsond['to_channels']=channels
        self.log('posting:',jsond)
        res=await self.api.post(jsond)
        if 'success' in res:
            self.root.change_screen('feed')
            return {'post_id':res['post_id']}
                    

    @property
    def keys(self):
        return self.api.keys
            
    async def get_post(self,post_id):
        return await self.api.get_post(post_id)

    async def get_posts(self,uri='/inbox/world'):
        self.log(f'app.get_posts(uri={uri} -> ...')
        data = await self.api.get_posts(uri)
        self.log('app.get_posts() got back from api.get_posts():',data)

        newdata=[]
        for d in data:
            self.log('data d:',d)
            if not 'val' in d: continue
            newdict = dict(d['val'].items())
            newdict['timestamp']=float(d['time'])
            newdata.append(newdict)
        
        # return index
        return newdata

    async def get_channel_posts(self,channel,prefix='inbox'):
        # am I allowed to?
        if not channel in self.keys:
            self.log('!! tsk tsk dont be nosy')
            return
        return await self.get_posts(uri=os.path.join(prefix,channel))

    async def get_channel_inbox(self,channel):
        return await self.get_channel_posts(channel=channel,prefix='inbox')
    
    async def get_channel_outbox(self,channel):
        return await self.get_channel_posts(channel=channel,prefix='outbox')

    async def get_my_posts(self,username=None):
        if username is None and self.username: username=self.username
        if not username:
            self.log(f'!! whose posts?')
            return
        self.log(f'get_my_posts({self.username})')
        return await self.get_channel(username)



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
