## CONFIG
# change this to your external ip address for your server
#(needs to be external to allow tor routing)
from config import *
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from comrad import *

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
# sys.path.insert(0,os.path.join(PATH_COMRAD_LIB,'KivyMD'))
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
from requests.exceptions import ReadTimeout

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

    def log(self,*x,**y): return self.app.log(*x,**y)

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
        self.app.screen_hist.append(self.app.screen)
        self.app.screen = self.screen = screen

        # toolbar
        toolbar=self.ids.toolbar
        action_items = toolbar.ids.right_actions.children
        for item in action_items:
            # this the screen?
            #self.log('ITEM!!',item, item.icon)
            if item.icon == SCREEN_TO_ICON[screen]:
                item.text_color=rgb(*COLOR_ACCENT)
            else:
                item.text_color=rgb(*COLOR_ICON)
        pass



    def change_screen_from_uri(self,uri,*args):
        self.app.uri=uri
        screen_name = route(uri)
        self.app.screen = screen_name
        self.app.log(f'routing to {screen_name}')
        self.scr_mngr.current = screen_name
    
    def view_post(self,post_id):
        self.post_id=post_id
        self.change_screen('view')

    # def refresh(self,*x,**yy):
    #     async def go():    
    #         if not hasattr(self.app,'is_logged_in') or not self.app.is_logged_in or not hasattr(self.app,'comrad') or not self.app.comrad:
    #             self.change_screen('login')
    #             self.app.log('changing screen???')
    #             return None


    #         logger.info(f'REFRESH: {self.app.is_logged_in}, {self.app.comrad.name}')
    #         self.app.log('<--',x,yy)
    #         if not hasattr(self.app,'map') or not self.app.map:
    #             from comrad.app.screens.map import MapWidget
    #             self.app.map=MapWidget()
    #         self.app.map.open()
    #         await self.app.comrad.get_updates()
    #         self.app.map.dismiss()
    #         self.app.map=None
    #     asyncio.create_task(go())




from comrad.app.screens.dialog import MDDialog2




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
        y['color_bg']=rgb(*COLOR_BG,a=0.5)
        y['type']='custom'
        y['overlay_color']=rgb(*COLOR_BG,a=0)  #rgb(*COLOR_BG)
        self.color_bg=rgb(*COLOR_BG)
        super().__init__(*x,**y)
        self.ok_to_continue=False
        self.dismissable=False
    
    def on_dismiss(self):
       if not self.dismissable:
           return True 
    
    def on_touch_down(self,touch):
        self.ok_to_continue=True
        logger.info('oof!')
        # if hasattr(self,'msg_dialog'):
            # logger.info(str(self.msg_dialog))


class TextInputPopupCard(MDDialog2):
    def say(self,x=None):
        self.ok_to_continue=True
        self.response=self.field.text
        return self.response


    def __init__(self,msg,password=False,input_name='',comrad_name='',*x,**y):
        self.ok_to_continue=False
        self.response=None
        title=msg
        from comrad.app.screens.login.login import UsernameField,PasswordField,UsernameLayout,UsernameLabel

        class TextInputPopupCardField(UsernameField):
            def on_text_validate(self):
                self.has_had_text = True
                self._set_text_len_error()

                # custom
                self.card.say()

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
        # self.field = PasswordField() if password else UsernameField()
        self.field = TextInputPopupCardField()
        self.field.card=self
        self.field.password=True
        self.field.line_color_focus=rgb(*COLOR_TEXT)
        self.field.line_color_normal=rgb(*COLOR_TEXT)
        self.field.font_name=FONT_PATH
        self.field.font_size='20sp'
        self.field.pos_hint={'center_y':0.5}

        


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
        self.size=('400sp','400sp')
        self.adaptive_height=True
        self.ids.text.font_size='28sp'
        for widget in self.ids.button_box.children:
            widget.font_size='18sp'

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
        self.ids.text.font_size='22sp'

        for widget in self.ids.button_box.children:
            widget.font_size='22sp'


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
    title = 'Comrad'
    logged_in=False
    login_expiry = 60 * 60 * 24 * 7  # once a week
    texture = ObjectProperty()
    uri='/do/login'
    screen='login'
    screen_hist=[]
    screen_names = [
        'feed',
        'messages',
        'post',
        'profile',
        # 'refresh',
        # 'login'
    ]

    def go_back(self):
        self.change_screen(
            self.screen_hist.pop() if self.screen_hist else 'feed'
        )

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        # self.log(f'keyboard:{keyboard}\nkeycode: {keycode}\ntext: {text}\ninstance: {instance}\nmodifiers:\n{modifiers}\n\n')
        
        ## arrows
        # ctrl left
        modifiers=set(modifiers)
        
        # enter? continue
        if keycode==40:
            if hasattr(self,'msg_dialog') and self.msg_dialog:
                self.msg_dialog.ok_to_continue=True

        # left
        if keycode == 80 and 'ctrl' in modifiers:
            # go back
            self.go_back()
        # down
        elif keycode==81 and 'ctrl' in modifiers:
            screen_index=self.screen_names.index(self.screen)
            new_screen = self.screen_names[screen_index - 1]
            
            self.change_screen(new_screen)
        # up
        elif keycode==82 and 'ctrl' in modifiers:
            screen_index=self.screen_names.index(self.screen)
            try:
                new_screen = self.screen_names[screen_index +1]
            except IndexError:
                new_screen = self.screen_names[0]

            self.change_screen(new_screen)
        
        
        ## keys
        elif text=='f' and 'ctrl' in modifiers:
            self.change_screen('feed')
        elif text=='m' and 'ctrl' in modifiers:
            self.change_screen('messages')
        elif text=='c' and 'ctrl' in modifiers:
            self.change_screen('post')
        elif text=='p' and 'ctrl' in modifiers:
            self.change_screen('profile')
        elif text=='r' and 'ctrl' in modifiers:
            self.change_screen('refresh')
        elif text=='e' and 'ctrl' in modifiers:
            self.change_screen('login')
        


    def rgb(self,*_): return rgb(*_)

    def change_screen(self, screen, *args):
        self.root.change_screen(screen,*args)

    def get_username(self): return self._name

    @property
    def crypt(self):
        if not hasattr(self,'_crypt'):
            from comrad.backend.crypt import Crypt
            self._crypt = Crypt(
                fn=PATH_CRYPT_CA_DATA,
                encrypt_values=False,
            )
        return self._crypt

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_loop_worker = None
        self.loop=asyncio.get_event_loop()
        self.comrad=None
        self._name=''
        Window.bind(on_key_down=self._on_keyboard_down)


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
        
        action_items = toolbar.ids.right_actions.children


        

        # build the walker
        self.walker=MazeWalker(callbacks=self.callbacks)
        self.torpy_logger = logging.getLogger('torpy')
        self.torpy_logger.propagate=False
        self.torpy_logger.addHandler(self.walker)
        import ipinfo
        ipinfo_access_token = '90df1baf7c373a'
        self.ipinfo_handler = ipinfo.getHandler(ipinfo_access_token)

        from comrad.app.screens.map import MapWidget
        self.map = MapWidget()
        
        self.change_screen(self.screen)

        for item in action_items:
            if item.icon == SCREEN_TO_ICON['login']:
                item.text_color=rgb(*COLOR_ACCENT)
            else:
                item.text_color=rgb(*COLOR_ICON)
        

        return self.root

    # def boot(self,username):
    #     commie = Comrad(username)
    #     if self.exists_locally_as_contact()

    def open_map(self):
        if self.map is None:
            from comrad.app.screens.map import MapWidget
            self.map = MapWidget()
            self.map.open()
    
    def close_map(self):
        if self.map is not None:
            self.map.dismiss()
            self.map=None

    @property
    def callbacks(self):
        return {
            'torpy_guard_node_connect':self.callback_on_hop,
            'torpy_extend_circuit':self.callback_on_hop,
        }
    
    async def callback_on_hop(self,rtr):
        if not hasattr(self,'hops'): self.hops=[]
        if not hasattr(self,'map') or not self.map:
            from comrad.app.screens.map import MapWidget
            self.map=MapWidget()
        if not self.map.opened:
            self.map.open()
            # self.map.draw()

        try:
            deets = self.ipinfo_handler.getDetails(rtr.ip)
            self.hops.append((rtr,deets))
            lat,long=tuple(float(_) for _ in deets.loc.split(','))
            flag=f'{deets.city}, {deets.country_name} ({rtr.nickname})'
            
            self.map.add_point(lat,long,flag)
            self.map.draw()
            # await asyncio.sleep(2)
            # logger.info('CALLBACK ON HOP: ' + flag)
        except ReadTimeout as e:
            self.log('!! read time out:',e)
            return

    def load_store(self):
        if not self.store.exists('user'): return
        userd=self.store.get('user')
        if not userd: return

        self.username = userd.get('username','')




    def clear_widget_tree(self,widget_type,widget=None):
        if not widget: widget=self.root
        for widg in widget.children:
            if hasattr(widg,'children') and widg.children:
                self.clear_widget_tree(widget_type,widget=widg)
            
            self.log(widg,type(widg),widget_type,issubclass(type(widg),widget_type))
            if issubclass(type(widg),widget_type):
                self.remove_widget(widg)


    def view_profile(self,username):
        self.username=username
        self.change_screen('profile')
        # self.username=self.comrad.name


















    


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
        contacts_obj = self.comrad.contacts()
        contacts = [p.name for p in contacts_obj]
        return contacts

    async def get_post(self,post_id):
        return self.comrad.read_post()

    def get_posts(self,uri=b'/inbox/world'):
        return self.comrad.posts()
        

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
        return await self.comrad.posts()



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

    async def get_input(self,msg,comrad_name='Telephone',get_pass=False,yesno=False,**y):
        from comrad.app.screens.feed.feed import PostCardInputPopup
        # if hasattr(self,'msg_dialog') and self.msg_dialog:# and hasattr(self.msg_dialog,'card') and self.msg_dialog.card:
        #     self.msg_dialog0=self.msg_dialog
        #     self.msg_dialog0.dismiss()
        #     self.msg_dialog0=None
        
        if yesno:
            self.msg_dialog = BooleanInputPopupCard(msg,comrad_name=comrad_name,**y)
            
        else:
            self.msg_dialog = TextInputPopupCard(msg,password=get_pass,comrad_name=comrad_name,**y)

        response = await self.msg_dialog.open()
        logger.info(f'get_input got user response {response}')
        if self.msg_dialog: 
            self.msg_dialog.dismiss()
        self.msg_dialog=None
        # async def task():
        #     await asyncio.sleep(1)
        #     self.msg_dialog.dismiss()
        #     self.msg_dialog=None
        # asyncio.create_task(task())
        return response

    async def ring_ring(self,*x,commie=None,**y):
        if not commie: commie=self.comrad
        from comrad.app.screens.map import MapWidget
        self.map=MapWidget()
        self.map.open()
        resp_msg_d = await commie.ring_ring(*x,**y)
        logger.info('done with ring_ring! ! !')
        self.map.dismiss()
        self.map=None
        return resp_msg_d

    
    async def get_updates(self,*x,commie=None,**y):
        if not commie: commie=self.comrad
        from comrad.app.screens.map import MapWidget
        self.map=MapWidget()
        self.map.open()
        await commie.get_updates(*x,**y)
        logger.info('done with get_updates! ! !')
        self.map.dismiss()
        self.map=None
        

        
    async def stat(self,msg,comrad_name='Telephone',pause=False,get_pass=False,**y):
        from comrad.app.screens.feed.feed import PostCard,PostCardPopup
        # if hasattr(self,'msg_dialog') and self.msg_dialog:# and hasattr(self.msg_dialog,'card') and self.msg_dialog.card:
        #     self.msg_dialog0=self.msg_dialog
        #     self.msg_dialog0.dismiss()
        #     self.msg_dialog0.clear_widgets()


        self.msg_dialog = MessagePopupCard()
        # self.root.add_widget(self.msg_dialog)
        # self.msg_dialog.ids.msg_label.text=msg
        nm = '?' if not self.comrad else self.comrad.name
        self.msg_dialog.card = postcard = PostCardPopup({
            'author':comrad_name,
            'author_prefix':'Comrad @',
            'to_name':nm,
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

        # if hasattr(self,'msg_dialog0'):
            # self.root.remove_widget(self.msg_dialog0)
            
        await asyncio.sleep(0.1)
        while not self.msg_dialog.ok_to_continue:
            await asyncio.sleep(0.1)
            # logger.info(str(postcard), postcard.ok_to_continue,'??')
        self.msg_dialog.dismissable=True
        self.msg_dialog.dismiss()
        self.msg_dialog.remove_widget(postcard)
        # self.root.remove_widget(self.msg_dialog)
        # self.root.clear_widgets()
        self.msg_dialog.card = postcard = self.msg_dialog = None
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
            self.remove_widget(self.msg_dialog)


    async def prompt_addcontact(self,post_data,screen=None,post_id=None,post_card=None):
        meet_name = post_data.get('meet_name')
        meet_uri = post_data.get('meet').decode()    
                
        yn=await self.get_input(f"Exchange public keys with {meet_name}? It will allow you and @{meet_name} to read and write encrypted messages to one another.",yesno=True)


        if screen:
            num_slides=len(screen.carousel.slides)
            i=screen.carousel.index
            self.log('changing slide??',num_slides,i)
            screen.carousel.index=(i+1 if i<num_slides else 0)
            if post_card is not None:
                screen.carousel.remove_widget(post_card)    
        
        if yn:
            fnfn = self.comrad.save_uri_as_qrcode(
                uri_id=meet_uri,
                name=meet_name
            )
            await self.stat(f'''Saved {meet_name}'s public key:\n{meet_uri}.''',img_src=fnfn)
            await self.stat('Now returning the invitation...')
            self.open_map()
            res = await self.comrad.meet_async(meet_name,returning=True)
            self.close_map()

            if res.get('success'):
                await self.stat('Invitation successfully sent.')
            else:
                await self.stat(res.get('status'))
            

        #delete this msg
        if post_id:
           self.comrad.delete_post(post_id)
        
        


    async def prompt_meet(self,meet_name,screen=None):
        yn=await self.get_input(f"Exchange public keys with {meet_name}? It will allow you and @{meet_name} to read and write encrypted messages to one another.",yesno=True)

        if yn:
            other_data = {}
            path_avatar=os.path.join(PATH_AVATARS,self.comrad.name+'.png')

            if os.path.exists(path_avatar):
                yn_avatar = await self.get_input(f'Send along your avatar? Otherwise, you will appear to {meet_name} as the default avatar.',yesno=True)

                if yn_avatar:
                    with open(path_avatar,'rb') as f:
                        other_data['img_avatar']=f.read()
                
                extra_msg = await self.get_input(f'Include a short message to {meet_name}? (optional)')
                other_data['extra_msg']=extra_msg.strip()
            await self.stat('Sending the invitation...')
            self.open_map()
            res = await self.comrad.meet_async(
                meet_name,
                returning=True,
                other_data=other_data
            )
            self.close_map()

            if res.get('success'):
                await self.stat('Invitation successfully sent.')
            else:
                await self.stat(res.get('status'))







if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(MainApp().app_func())
    except AssertionError:
        print('\n\nGoodbye.\n')
        pass
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
