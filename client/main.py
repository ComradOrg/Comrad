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

Window.size = WINDOW_SIZE

def log(*args):
    with open('log.txt','a+') as of:
        of.write(' '.join([str(x) for x in args])+'\n')



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

def get_async_tor_proxy_session():
    from requests_futures.sessions import FuturesSession
    session = FuturesSession()
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
    api = 'http://%s/api' % SERVER_ADDR
    #api = 'http://komrades.net:5555/api'
    logged_in=False
    store = JsonStore('komrade.json')
    login_expiry = 60 * 60 * 24 * 7  # once a week
    #login_expiry = 5 # 5 seconds

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
        self.username=''
        # bind 
        global app,root
        app = self
        #self.username = self.store.get('userd').get('username')
        self.load_store()
        self.root = root = Builder.load_file('root.kv')
        
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
            log(self.username)
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
        self.store.put('user',username=un,logged_in=True,logged_in_when=time.time())
        self.root.change_screen('feed')


    def login(self,un=None,pw=None):
        url = self.api+'/login'

        with self.get_session() as sess:
            #res = requests.post(url, json={'name':un, 'passkey':pw})
            res = sess.post(url, json={'name':un, 'passkey':pw})
            log(res.text)

            if res.status_code==200:
                data=res.json()
                self.save_login(un)
                return True
            else:
                # self.root.ids.login_status.text=res.text
                return False

    def register(self,un,pw):
        url = self.api+'/register'

        with self.get_session() as sess:
            #res = requests.post(url, json={'name':un, 'passkey':pw})
            res = sess.post(url, json={'name':un, 'passkey':pw})
            if res.status_code==200:
                self.save_login(un)
            else:
                pass
                #self.root.ids.login_status.text=res.text

    
    def upload(self,orig_img_src):
        url_upload=self.api+'/upload'
        filename=orig_img_src[0] if orig_img_src and os.path.exists(orig_img_src[0]) else ''
        if not filename: return
        
        server_filename=''
        media_uid=None
            
        with self.get_session() as sess:
            with sess.post(url_upload,files={'file':open(filename,'rb')}) as r1:
                if r1.status_code==200:
                    rdata1 = r1.json()
                    server_filename = rdata1.get('filename','')
                    media_uid=rdata1.get('media_uid')
                    if server_filename:
                        # pre-cache
                        cache_filename = os.path.join('cache','img',server_filename)
                        cache_filedir = os.path.dirname(cache_filename)
                        if not os.path.exists(cache_filedir): os.makedirs(cache_filedir)
                        shutil.copyfile(filename,cache_filename)

        return {'cache_filename':cache_filename, 'media_uid':media_uid, 'server_filename':server_filename}
        
        
    
    def post(self, content='', media_uid=None):
        timestamp=time.time()
        jsond = {'content':str(content),'media_uid':media_uid,
                 'username':self.username, 'timestamp':timestamp}

        url_post = self.api+'/post'
            
        with self.get_session() as sess:
            # post    
            with sess.post(url_post, json=jsond) as r2:
                log('got back from post: ' + r2.text)
                rdata2 = r2.json()
                post_id = rdata2.get('post_id',None)
                if post_id:
                    # pre-cache
                    cache_dir = os.path.join('cache','json',post_id[:3])
                    cache_fnfn = os.path.join(cache_dir,post_id[3:]+'.json')
                    if not os.path.exists(cache_dir): os.makedirs(cache_dir)
                    with open(cache_fnfn,'w') as of:
                        json.dump(jsond, of)
                    
                    #self.root.view_post(post_id)
                    self.root.change_screen('feed')
        return {'post_id':post_id}
                    

                    
            

    def get_post(self,post_id):
        # get json from cache?
        ofn_json = os.path.join('cache','json',str(post_id)+'.json')
        if os.path.exists(ofn_json):
            with open(ofn_json) as f:
                jsond = json.load(f)
        else:
            with self.get_session() as sess:
                with sess.get(self.api+'/post/'+str(post_id)) as r:
                    jsond = r.json()

                    # cache it!
                    with open(ofn_json,'w') as of:
                        json.dump(jsond, of)
        
        return jsond

    def get_posts(self):
        with self.get_session() as sess:
            with sess.get(self.api+'/posts') as r:
                log(r.text)
                jsond=r.json()
                return jsond['posts']
        return []

    def get_posts_async(self):
        result=[]
        with self.get_session() as sess:
            futures = [sess.get(self.api+'/posts')]
            for future in as_completed(futures):
                log('second?')
                r=future.result()
                log(r.text)
                jsond=r.json()
                result=jsond['posts']
            log('first?')
        return result
        
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
    App = MainApp()
    App.run()
