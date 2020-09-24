## CONFIG
# change this to your external ip address for your server
#(needs to be external to allow tor routing)
from config import *
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *

import logging
logger=logging.getLogger(__name__)

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

# prefer experimental kivy if possible
# sys.path.insert(0,os.path.join(PATH_KOMRADE_LIB,'KivyMD'))
import kivymd
# print(kivymd.__file__)
# exit()


# imports
from kivy.uix.screenmanager import *
from kivymd.app import *
from kivymd.uix.button import *
from kivymd.uix.toolbar import *
from kivymd.uix.screen import *
from kivymd.uix.dialog import *
from kivy.lang import *
from kivy.uix.boxlayout import *
from kivymd.theming import *
from kivy.properties import *
from kivymd.uix.label import *
from kivy.uix.widget import *
from kivymd.uix.list import *
from kivymd.uix.card import *
from kivymd.uix.boxlayout import *
from kivy.uix.gridlayout import *
from kivy.metrics import *
from kivy.properties import *   
from kivymd.uix.list import * #MDList, ILeftBody, IRightBody, ThreeLineAvatarListItem, TwoLineAvatarListItem, BaseListItem, ImageLeftWidget
from kivy.uix.image import *
import requests,json
from kivy.storage.jsonstore import *
from kivy.core.window import *
from kivy.core.text import *
import shutil,sys
from kivy.uix.image import *
import sys
sys.path.append("..") # Adds higher directory to python modules path.

from kivy.event import *
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
        self.app.uri=uri
        screen_name = route(uri)
        self.app.screen = screen_name
        self.app.log(f'routing to {screen_name}')
        self.scr_mngr.current = screen_name
    
    def view_post(self,post_id):
        self.post_id=post_id
        self.change_screen('view')






from komrade.app.screens.dialog import MDDialog2




class ProgressPopup(MDDialog2): pass


class MessagePopup(MDDialog2):
    pass
    # def __init__(self,*x,**y):
    #     super().__init__(*x,**y)
    #     self.ok_to_continue=False
    
    # def on_dismiss(self):
    #     if not self.ok_to_continue:
    #         self.ok_to_continue=True
    #         logger.info('ouch!')
        



    pass
class MessagePopupCard(MDDialog2):
    def __init__(self,*x,**y):
        # y['color_bg']=rgb(*COLOR_CARD)
        y['type']='custom'
        y['overlay_color']=(0,0,0,0)
        super().__init__(*x,**y)
        # self.color_bg=rgb(*COLOR_CARD)
        self.ok_to_continue=False
    
    def on_dismiss(self):
       return True
    
    def on_touch_down(self,touch):
        self.ok_to_continue=True
        logger.info('oof!')
        # if hasattr(self,'msg_dialog'):
            # logger.info(str(self.msg_dialog))



class TextInputPopupCard(MDDialog2):
    def say(self,x):
        self.ok_to_continue=True
        self.response=self.field.text
        return self.response


    def __init__(self,msg,password=False,input_name='',komrade_name='',*x,**y):
        self.ok_to_continue=False
        self.response=None
        title=msg
        from komrade.app.screens.login.login import UsernameField,PasswordField,UsernameLayout,UsernameLabel

        self.layout=MDBoxLayout()
        self.layout.orientation='vertical'
        self.layout.cols=1
        self.layout.size_hint=('333sp','222sp')
        # self.layout.md_bg_color=(1,1,0,1)
        self.layout.adaptive_height=True
        self.layout.height=self.layout.minimum_height
        self.layout.spacing='0sp'
        self.layout.padding='0sp'

        # self.layout.size=('333sp','333sp')



        self.field_layout=UsernameLayout()
        self.field = PasswordField() if password else UsernameField()
        self.field.line_color_focus=rgb(*COLOR_TEXT)
        self.field.line_color_normal=rgb(*COLOR_TEXT,a=0.25)
        self.field.font_name=FONT_PATH
        self.field.font_size='20sp'

        self.field_label = UsernameLabel(text='password:' if password else input_name)
        self.field_label.font_name=FONT_PATH
        self.field_label.font_size='20sp'
        
        if title:
            self.title_label = UsernameLabel(text=title)
            self.title_label.halign='center'
            self.title_label.font_size='20sp'
            self.title_label.pos_hint={'center_x':0.5}
            self.title_label.font_name=FONT_PATH
            #self.field_layout.add_widget(self.title_label)
            self.layout.add_widget(self.title_label)
            

        
        self.field_layout.add_widget(self.field_label)
        self.field_layout.add_widget(self.field)
        self.layout.add_widget(self.field_layout)
        # do dialog's intro
        super().__init__(
            type='custom',
            text=msg,
            content_cls=self.layout,
            buttons=[
                MDFlatButton(
                    text="cancel",
                    text_color=rgb(*COLOR_TEXT),
                    md_bg_color = (0,0,0,1),
                    theme_text_color='Custom',
                    on_release=self.dismiss,
                    font_name=FONT_PATH
                ),
                MDFlatButton(
                    text="enter",
                    text_color=rgb(*COLOR_TEXT),
                    md_bg_color = (0,0,0,1),
                    theme_text_color='Custom',
                    on_release=self.say,
                    font_name=FONT_PATH
                ),
            ],
            color_bg = rgb(*COLOR_CARD)
        )
        self.ids.text.text_color=rgb(*COLOR_TEXT)
        self.ids.text.font_name=FONT_PATH
        self.size=('333sp','111sp')
        self.adaptive_height=True

    # wait and show
    async def open(self,maxwait=666,pulse=0.1):
        super().open()
        await asyncio.sleep(pulse)
        waited=0
        while not self.ok_to_continue:
            await asyncio.sleep(pulse)
            waited+=pulse
            if waited>maxwait: break
            # logger.info(f'waiting for {waited} seconds... {self.ok_to_continue} {self.response}')
        return self.response














class BooleanInputPopupCard(MDDialog2):
    def say_yes(self,x):
        # logger.info('say_yes got:',str(x))
        self.ok_to_continue=True
        self.response=True
        return self.response
    def say_no(self,x):
        # logger.info('say_no got:',str(x))
        self.ok_to_continue=True
        self.response=False
        return self.response
    
    def __init__(self,msg,*x,**y):
        self.ok_to_continue=False
        self.response=None
        

        # do dialog's intro
        super().__init__(
            text=msg,
            buttons=[
                MDFlatButton(
                    text="no",
                    text_color=rgb(*COLOR_TEXT),
                    md_bg_color = (0,0,0,1),
                    theme_text_color='Custom',
                    on_release=self.say_no,
                    font_name=FONT_PATH
                ),
                MDFlatButton(
                    text="yes",
                    text_color=rgb(*COLOR_TEXT),
                    md_bg_color = (0,0,0,1),
                    theme_text_color='Custom',
                    on_release=self.say_yes,
                    font_name=FONT_PATH
                ),
            ],
            color_bg = rgb(*COLOR_CARD)
        )

        self.ids.text.text_color=rgb(*COLOR_TEXT)
        self.ids.text.font_name=FONT_PATH

    # wait and show
    async def open(self,maxwait=666,pulse=0.1):
        super().open()
        await asyncio.sleep(pulse)
        waited=0
        while not self.ok_to_continue:
            await asyncio.sleep(pulse)
            waited+=pulse
            if waited>maxwait: break
            # logger.info(f'waiting for {waited} seconds... {self.ok_to_continue} {self.response}')
        return self.response


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

class MainApp(MDApp, Logger):
    title = 'Komrade'
    logged_in=False
    login_expiry = 60 * 60 * 24 * 7  # once a week
    texture = ObjectProperty()
    uri='/do/login'

    def rgb(self,*_): return rgb(*_)

    def change_screen(self, screen, *args):
        self.screen=screen
        self.root.change_screen(screen,*args)

    def get_username(self): return self._name

    @property
    def crypt(self):
        if not hasattr(self,'_crypt'):
            from komrade.backend.crypt import Crypt
            self._crypt = Crypt(
                fn=PATH_CRYPT_CA_DATA,
                encrypt_values=False,
            )
        return self._crypt

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_loop_worker = None
        self.loop=asyncio.get_event_loop()
        
        # connect to API
        self.komrade=None
        self._name=''


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

        # build the walker
        self.walker=MazeWalker(callbacks=self.callbacks)
        self.torpy_logger = logging.getLogger('torpy')
        self.torpy_logger.propagate=False
        self.torpy_logger.addHandler(self.walker)
        import ipinfo
        ipinfo_access_token = '90df1baf7c373a'
        self.ipinfo_handler = ipinfo.getHandler(ipinfo_access_token)

        from komrade.app.screens.map import MapWidget
        self.map = MapWidget()
        
        return self.root

    # def boot(self,username):
    #     kommie = Komrade(username)
    #     if self.exists_locally_as_contact()

    @property
    def callbacks(self):
        return {
            'torpy_guard_node_connect':self.callback_on_hop,
            'torpy_extend_circuit':self.callback_on_hop,
        }
    
    async def callback_on_hop(self,rtr):
        if not hasattr(self,'hops'): self.hops=[]
        if not self.map.opened:
            self.map.open()
            # self.map.draw()

        deets = self.ipinfo_handler.getDetails(rtr.ip)
        self.hops.append((rtr,deets))
        lat,long=tuple(float(_) for _ in deets.loc.split(','))
        flag=f'{deets.city}, {deets.country_name} ({rtr.nickname})'
        
        self.map.add_point(lat,long,flag)
        self.map.draw()
        import asyncio
        # await asyncio.sleep(2)
        logger.info('CALLBACK ON HOP: ' + flag)

    def load_store(self):
        if not self.store.exists('user'): return
        userd=self.store.get('user')
        if not userd: return

        self.username = userd.get('username','')
    


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
    
    async def post(self, content='', file_id=None, file_ext=None, anonymous=False,channel='world'):
        #timestamp=time.time()
        jsond={}
        #jsond['timestamp']=
        if content: jsond['content']=str(content)
        if file_id: jsond['file_id']=str(file_id)
        if file_ext: jsond['file_ext']=str(file_ext)
        if channel and channel[0]=='@': channel=channel[1:]
        self.log(f'''app.post(
            content={content},
            file_id={file_id},
            file_ext={file_ext},
            anonymous={anonymous},
            channel={channel},
            [username={self.username}]'''
        )
        if not anonymous and self.username:
            jsond['author']=self.username
        
        #jsond['channel']=channel
        self.log('posting:',jsond)
        res=await self.api.post(jsond,channel = channel)
        if 'success' in res:
            self.root.change_screen('feed')
            return {'post_id':res['post_id']}
                    

    @property
    def keys(self):
        return self.komrade.contacts()
            
    async def get_post(self,post_id):
        return self.komrade.read_post()

    def get_posts(self,uri=b'/inbox/world'):
        return self.komrade.posts()
        

    async def get_channel_posts(self,channel,prefix='inbox'):
        # am I allowed to?
        if not channel in self.keys:
            self.log('!! tsk tsk dont be nosy')
            return
        return await self.get_posts(uri='/'+os.path.join(prefix,channel))

    async def get_channel_inbox(self,channel):
        return await self.get_channel_posts(channel=channel,prefix='inbox')
    
    async def get_channel_outbox(self,channel):
        return await self.get_channel_posts(channel=channel,prefix='outbox')

    async def get_my_posts(self):
        return await self.persona.read_outbox()



    ### SYNCHRONOUS?
    def app_func(self):
        '''This will run both methods asynchronously and then block until they
        are finished
        '''
        # self.other_task = asyncio.ensure_future(self.waste_time_freely())
        # self.other_task = asyncio.ensure_future(self.api.connect_forever())

        async def run_wrapper():
            # we don't actually need to set asyncio as the lib because it is
            # the default, but it doesn't hurt to be explicit
            await self.async_run() #async_lib='asyncio')
            print('App done')
            # self.other_task.cancel()

        # return asyncio.gather(run_wrapper(), self.other_task)
        asyncio.run(run_wrapper())



    def open_dialog(self,msg):
        if not hasattr(self,'dialog') or not self.dialog:
            self.dialog = ProgressPopup()
        
        # raise Exception(self.dialog, msg)
        self.dialog.text=msg
        self.dialog.open()
        #stop

    async def get_input(self,msg,komrade_name='Telephone',get_pass=False,yesno=False,**y):
        from komrade.app.screens.feed.feed import PostCardInputPopup
        if hasattr(self,'msg_dialog') and self.msg_dialog:# and hasattr(self.msg_dialog,'card') and self.msg_dialog.card:
            self.msg_dialog0=self.msg_dialog
            self.msg_dialog0.dismiss()
            self.msg_dialog0=None
        
        if yesno:
            self.msg_dialog = BooleanInputPopupCard(msg,komrade_name=komrade_name,**y)
        else:
            self.msg_dialog = TextInputPopupCard(msg,password=get_pass,komrade_name=komrade_name,**y)

        response = await self.msg_dialog.open()
        logger.info(f'get_input got user response {response}')
        async def task():
            await asyncio.sleep(1)
            self.msg_dialog.dismiss()
        asyncio.create_task(task())
        return response

    async def ring_ring(self,*x,kommie=None,**y):
        if not kommie: kommie=self.komrade
        from komrade.app.screens.map import MapWidget
        self.map=MapWidget()
        self.map.open()
        resp_msg_d = await kommie.ring_ring(*x,**y)
        logger.info('done with ring_ring! ! !')
        self.map.dismiss()
        self.map=None
        return resp_msg_d

    
    async def get_updates(self,*x,kommie=None,**y):
        if not kommie: kommie=self.komrade
        from komrade.app.screens.map import MapWidget
        self.map=MapWidget()
        self.map.open()
        await kommie.get_updates(*x,**y)
        logger.info('done with get_updates! ! !')
        self.map.dismiss()
        self.map=None
        

        
    async def stat(self,msg,komrade_name='Telephone',pause=False,get_pass=False,**y):
        from komrade.app.screens.feed.feed import PostCard,PostCardPopup
        if hasattr(self,'msg_dialog') and self.msg_dialog:# and hasattr(self.msg_dialog,'card') and self.msg_dialog.card:
            self.msg_dialog0=self.msg_dialog
            self.msg_dialog0.dismiss()


        self.msg_dialog = MessagePopupCard()
        # self.msg_dialog.ids.msg_label.text=msg

        self.msg_dialog.card = postcard = PostCardPopup({
            'author':komrade_name,
            'author_prefix':'@',
            'to_name':'me',
            'content':msg,
            'timestamp':time.time(),
            'author_label_font_size':'18sp',
            **y
        },
        msg_dialog=self.msg_dialog)
        postcard.font_size='16sp'
        postcard.size_hint=(None,None)
        postcard.size=('600sp','600sp')
        postcard.ok_to_continue=False

        self.msg_dialog.add_widget(postcard)

        self.msg_dialog.open(animation=False)

        if hasattr(self,'msg_dialog0'):
            self.root.remove_widget(self.msg_dialog0)
            if hasattr(self.msg_dialog0,'card'):
                self.msg_dialog0.remove_widget(self.msg_dialog0.card)
            
        await asyncio.sleep(0.1)
        while not self.msg_dialog.ok_to_continue:
            await asyncio.sleep(0.1)
            # logger.info(str(postcard), postcard.ok_to_continue,'??')
        # self.msg_dialog.dismiss()
        # self.msg_dialog.remove_widget(postcard)
        # self.msg_dialog.card = postcard = self.msg_dialog = None
        await asyncio.sleep(0.1)
        return {'success':True, 'status':'Delivered popup message'}
        

    def open_msg_dialog(self,msg):
        # from screens.post.post import MessagePopup,ProgressPopup
        if not hasattr(self,'msg_dialog') or not self.msg_dialog:
            self.msg_dialog = MessagePopup()
            self.msg_dialog.ids.msg_label.text=msg
            self.msg_dialog.open()

    def close_dialog(self):
        if hasattr(self,'dialog'):
            self.dialog.dismiss()

    def close_msg_dialog(self):
        if hasattr(self,'msg_dialog'):
            self.msg_dialog.remove_widget(self.msg_dialog.card)
            self.msg_dialog.dismiss()








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
