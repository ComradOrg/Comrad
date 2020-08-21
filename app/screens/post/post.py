from screens.base import ProtectedScreen,BaseScreen
from plyer import filechooser
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDRaisedButton,MDFillRoundFlatButton,MDRoundFlatIconButton
from kivy.properties import ListProperty,ObjectProperty
from kivy.app import App
from screens.feed.feed import *
import os,time,threading
from threading import Thread
from kivymd.uix.dialog import MDDialog
from kivy.core.image import Image as CoreImage
from kivymd.uix.gridlayout import MDGridLayout
import io,shutil,asyncio
from kivymd.uix.chip import MDChip
from main import rgb,COLOR_TEXT,COLOR_ACCENT,COLOR_CARD,COLOR_INACTIVE,COLOR_ACTIVE
from misc import *
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout

from kivymd.theming import ThemableBehavior
from kivymd.uix.button import MDIconButton
from kivymd.uix.stacklayout import MDStackLayout
from main import COLOR_TEXT,rgb,COLOR_ICON,COLOR_ACCENT,COLOR_INACTIVE

class ProgressPopup(MDDialog): pass
class MessagePopup(MDDialog): pass

class UploadButton(MDRectangleFlatButton):
    '''
    Button that triggers 'filechooser.open_file()' and processes
    the data response from filechooser Activity.
    '''

    selection = ListProperty([])

    def choose(self):
        '''
        Call plyer filechooser API to run a filechooser Activity.
        '''
        filechooser.open_file(on_selection=self.handle_selection)

    def handle_selection(self, selection):
        '''
        Callback function for handling the selection response from Activity.
        '''
        self.selection = selection



    def on_selection(self, *a, **k):
        '''
        Update TextInput.text after FileChoose.selection is changed
        via FileChoose.handle_selection.
        '''
        pass
        #App.get_running_app().root.ids.result.text = str(self.selection)

class AddPostTextField(MDTextField): pass
class ButtonLayout(MDBoxLayout): pass
class PostButton(MDRectangleFlatButton): pass
class PostStatus(MDRectangleFlatButton): pass


class SelectAddressee(DropDownWidget):
    def __init__(self, wordlist, **kwargs):
        super().__init__(**kwargs)
        self.pos_hint = {'center_x':.5,'center_y':.5}
        self.size_hint = (None, None)
        self.size = (600, 60)
        
        self.ids.txt_input.word_list = wordlist
        self.ids.txt_input.starting_no = 1







class ChannelLayout(MDStackLayout):
    pass



class ChannelChip(MDRoundFlatIconButton):
    def callback(self):
        val=self.check if hasattr(self,'check') else False
        self.check = not val
        self.icon='checkbox-blank-outline' if self.check else 'check-box-outline'
        # self.md_bg_color=rgb(*COLOR_INACTIVE) if not self.check else rgb(*COLOR_ACTIVE)
        # raise Exception(['GOT VALL',val])
    pass
        
        
    # def on_icon(self, instance, value):
    #     self.log('on_icon',instance,value)
    #     if value == "":
    #         self.icon = "check-box-outline"
    #         self.remove_widget(self.ids.icon)
 

    # def on_touch_down(self, touch):
    #     colorobj=self.children[1]
    #     if not self.check:
    #         self.check=True
    #         self.icon="check-box-outline"
    #         self.color=rgb(*COLOR_ACTIVE)
    #         self.selected_chip_color=rgb(*COLOR_ACTIVE)
    #         colorobj.md_bg_color=rgb(*COLOR_ACTIVE)
    #         self.log(f'check = {self.check} and icon = {self.icon} and color = {self.color}')
    #     else:
    #         self.selected_chip_color=rgb(*COLOR_INACTIVE)
    #         self.check=False
    #         self.icon="checkbox-blank-outline"
    #         self.color=rgb(*COLOR_INACTIVE)
    #         colorobj.md_bg_color=rgb(*COLOR_INACTIVE)
    #         self.log(f'check = {self.check} and icon = {self.icon} and color = {self.color}')
    #         self.md_bg_color=rgb(*COLOR_INACTIVE)
    #     self.parent.parent.to_channels[self.label]=self.check

            # self.color=rgb(*COLOR_ACCENT) if self.check else (rgb(50,50,50))
            # self.log(md_choose_chip.parent.to_channels)
            # self.ids.chiplayout.md_bg_color=self.color
            
            # if self.selected_chip_color:
            #     Animation(
            #         color=self.theme_cls.primary_dark
            #         if not self.selected_chip_color
            #         else self.selected_chip_color,
            #         d=0.3,
            #     ).start(self)
            # if issubclass(md_choose_chip.__class__, MDChooseChip):
            #     for chip in md_choose_chip.children:
            #         if chip is not self:
            #             chip.color = self.theme_cls.primary_color
            # if self.check:
            #     if not len(self.ids.box_check.children):
            #         self.ids.box_check.add_widget(
            #             MDIconButton(
            #                 icon="check-box-outline",
            #                 size_hint_y=None,
            #                 height=dp(20),
            #                 disabled=True,
            #                 user_font_size=dp(20),
            #                 pos_hint={"center_y": 0.5},
            #             )
            #         )
            #     else:
            #         check = self.ids.box_check.children[0]
            #         self.ids.box_check.remove_widget(check)
            # if self.callback:
            #     self.callback(self, self.label)





class PostScreen(ProtectedScreen): 
    post_id = ObjectProperty()

    def on_pre_enter(self):
        super().on_pre_enter()
        
        # clear
        if hasattr(self,'post_status'): self.remove_widget(self.post_status)
        if hasattr(self,'post_textfield'): self.post_textfield.text=''

        post_json = {'author':self.app.username, 'timestamp':time.time()}
        self.post_card = post = PostCard(post_json)
        self.post_textfield = post_TextField = AddPostTextField()
        post_TextField.line_color_focus=rgb(*COLOR_TEXT)
        post_TextField.line_color_normal=rgb(*COLOR_TEXT)
        post_TextField.current_hint_text_color=rgb(*COLOR_TEXT)
        post_TextField.font_name='assets/overpass-mono-regular.otf'
        post_TextField.hint_text='word?'

        #self.addressee = SelectAddressee(list(self.app.keys.keys()))
        #post.add_widget(self.addressee)

        # post.remove_widget(post.scroller)
        self.channel_layout = ChannelLayout() #MDBoxLayout(size_hint=(1,None),orientation='horizontal',cols=3)
        # self.channel_layout.orientation='horizontal'
        # self.channel_layout.cols=1
        # self.channel_layout.size_hint=(1,None)
        # self.channel_layout.adaptive_height=True
        # self.channel_layout.adaptive_=True
        # self.channel_layout.spacing='20dp'
        # self.channel_layout.padding='15dp'
        # self.channel_layout.height='300sp' #self.channel_layout.minimum_height
        
        post.add_widget(self.channel_layout,1)
        self.post_card.to_channels = {}
        for channel in self.app.keys:
            chip = ChannelChip()
            # chip.ids.icon.width='26sp'
            self.log(f'adding channel {channel}')
            chip.text = '@'+channel
            # chip.color=rgb(*COLOR_INACTIVE)
            # chip.ids.chiplayout.md_bg_color=chip.color
            # chip.width='100sp'
            chip.font_name='assets/font.otf'
            chip.md_bg_color=rgb(*COLOR_INACTIVE)
            # chip.theme_text_color='Custom'
            # chip.text_color=rgb(*COLOR_INACTIVE)
            self.channel_layout.add_widget(chip)
            self.post_card.to_channels[channel]=False



        post.scroller.remove_widget(post.post_content)
        post.scroller.add_widget(post_TextField)
        post.scroller.size=('300dp','300dp')
        self.add_widget(post)

        self.button_layout = ButtonLayout()
        self.upload_button = UploadButton()
        self.upload_button.screen = self
        self.post_button = PostButton()
        self.post_button.screen = self
        self.post_status = PostStatus()
        self.post_status_added = False

        self.button_layout.add_widget(self.upload_button)
        self.button_layout.add_widget(self.post_button)
       

        self.post_button.md_bg_color=(0,0,0,1)
        self.upload_button.md_bg_color=(0,0,0,1)
        self.post_status.md_bg_color=(0,0,0,1)
        
        self.add_widget(self.button_layout)
        # self.add_widget(self.post_status)

    

    def write_post_status(self,x):
        self.post_status.text=str(x)
        if not self.post_status_added:
            self.add_widget(self.post_status)
            self.post_status_added=True

    def open_dialog(self,msg):
        if not hasattr(self,'dialog') or not self.dialog:
            self.dialog = ProgressPopup()
        self.dialog.ids.progress_label.text=msg
        self.dialog.open()

    def open_msg_dialog(self,msg):
        if not hasattr(self,'msg_dialog') or not self.msg_dialog:
            self.msg_dialog = MessagePopup()
        self.msg_dialog.ids.msg_label.text=msg
        self.msg_dialog.open()

    def close_dialog(self):
        if hasattr(self,'dialog'):
            self.dialog.dismiss()

    def close_msg_dialog(self):
        if hasattr(self,'msg_dialog'):
            self.msg_dialog.dismiss()


    def choose(self):
        # time.sleep(5)
        
        self.upload_button.choose()
        self.orig_img_src = self.upload_button.selection
        # self.open_dialog('uploading')
        # self.upload()
        # self.close_dialog()
        #mythread = threading.Thread(target=self.upload)
        #mythread.start()
        self.upload()

    def upload(self):
        # get file id
        filename=self.orig_img_src[0] if self.orig_img_src and os.path.exists(self.orig_img_src[0]) else ''
        if not filename: return
        self.img_id = file_id = get_random_id()
        self.img_ext = os.path.splitext(filename)[-1][1:]

        # cache
        tmp_img_fn = 'cache/'+self.img_id[:3]+'/'+self.img_id[3:]+'.'+self.img_ext
        tmp_img_dir = os.path.dirname(tmp_img_fn)
        if not os.path.exists(tmp_img_dir): os.makedirs(tmp_img_dir)
        shutil.copyfile(filename, tmp_img_fn)

        # add
        self.add_image(tmp_img_fn)
        
        # upload
        #def do_upload():
            
        asyncio.create_task(self.app.upload(tmp_img_fn, file_id=file_id))

        # Thread(target=do_upload).start()
        
        # self.close_dialog()

    def add_image(self,filename):
        if hasattr(self,'image_layout'):
            self.post_card.remove_widget(self.image_layout)
        
        self.image_layout = image_layout = PostImageLayout()
        self.image = image = PostImage(source=filename)
        # self.image.texture = img.texture
        self.image.height = '300dp'
        self.image_layout.add_widget(self.image)
        self.image_layout.height='300dp'
        self.post_card.add_widget(self.image_layout,index=1)

        

    def post(self):
        # check?
        maxlen = 500
        content = self.post_textfield.text
        lencontent = content.strip().replace('  ',' ').count(' ')
        # maxlen = int(self.post_textfield.max_text_length)
        lendiff = lencontent - maxlen
        if lendiff>0:
            self.open_msg_dialog(f'Text is currently {lencontent} words long, which is {lendiff} over the maximum text length of {maxlen} words.\n\n({lencontent}/{maxlen})')
            return

        # log('?????????????????'+self.media_uid)
        # if not hasattr(self,'img_id') and self.upload_button.selection:
        #     log('REUPLOADING')
        #     self.upload()

        async def do_post():
            file_id = self.img_id if hasattr(self,'img_id') else None
            file_ext = self.img_ext if hasattr(self,'img_ext') else None
            await self.app.post(content=content, file_id=file_id, file_ext=file_ext)
            import time
            self.close_dialog()
        
        self.open_dialog('posting')
        #Thread(target=do_post).start()
        asyncio.create_task(do_post())        

# class ViewPostScreen(ProtectedScreen): 
#     post_id = ObjectProperty()

#     def on_pre_enter(self):
#         for child in self.children:
#             log('child: '+str(child))
#             self.remove_widget(child)
        
#         post_json = self.app.get_post(self.root.post_id)
#         post = PostCard(post_json)
#         self.add_widget(post)

#     def on_enter(self):
#         for child in self.children: child.load_image()
        
    
#     pass
 


def get_random_id():
    import uuid
    return uuid.uuid4().hex