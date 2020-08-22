from screens.base import ProtectedScreen,BaseScreen
from plyer import filechooser
from kivy.uix.button import Button
from kivymd.uix.button import *
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
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.menu import MDDropdownMenu
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

def logg(*x):
    with open('log.txt','a+') as of: of.write(' '.join(str(y) for y in x)+'\n')

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


class PostScreen(ProtectedScreen): 
    post_id = ObjectProperty()

    def open_author_option(self):
        import kivy
        try:
            self.post_card.add_widget(self.to_whom_btn,1)
            self.to_whom_btn.height='100dp'
            self.to_whom_btn.size_hint_y=None
        except kivy.uix.widget.WidgetException:
            return
    
    def close_author_option(self):
        self.post_card.remove_widget(self.to_whom_btn)
        self.to_whom_btn.height='0dp'
        self.to_whom_btn.size_hint_y=None



    def on_pre_enter(self):
        super().on_pre_enter()
        self.to_channels = {}
        
        # clear
        if hasattr(self,'post_status'): self.remove_widget(self.post_status)
        if hasattr(self,'post_textfield'): self.post_textfield.text=''

        post_json = {'author':self.app.username, 'timestamp':time.time()}
        key=list(self.app.keys.keys())[0]
        post_json['to_name']='...?'
        
        self.post_card = post = PostCard(post_json)
        self.post_card.add_widget(get_separator('15sp'),1)
        self.post_card.add_widget(get_separator('15sp'),1)
        self.post_textfield = post_TextField = AddPostTextField()
        post_TextField.line_color_focus=rgb(*COLOR_TEXT)
        post_TextField.line_color_normal=rgb(*COLOR_TEXT)
        post_TextField.current_hint_text_color=rgb(*COLOR_TEXT)
        post_TextField.font_name='assets/overpass-mono-regular.otf'
        post_TextField.hint_text='word?'

        self.to_whom_btn = DropDownWidget(
            pos_hint = {'x':0,'center_y':.5},
            size_hint = (None, None),
        )
        inp_towhom = self.to_whom_btn.ids.txt_input
        inp_towhom.size_hint=(None,None)
        inp_towhom.width = '100sp'
        inp_towhom.font_name='assets/font.otf'
        # inp_towhom.height = '75sp'
        inp_towhom.adaptive_height=True
        inp_towhom.md_bg_color=rgb(*COLOR_CARD)
        # self.post_card.author_section_layout.md_bg_color=1,0,0,1
        self.to_whom_layo = MDBoxLayout()
        self.to_whom_layo.cols=1
        # self.to_whom_layo.size_hint=(None,None)
        self.to_whom_layo.width='300sp'
        self.to_whom_layo.height='2000sp'
        self.to_whom_layo.md_bg_color=1,1,0,1
        # self.post_card.author_section_layout.add_widget(MDLabel(text='-->'),1)
        # self.post_card.author_section_layout.add_widget(self.to_whom_btn)


        # self.to_whom_layo.add_widget(self.to_whom_btn)
        # self.tmp_msg = MDLabel(text='-->')
        self.post_card.add_widget(self.to_whom_btn,1)
        
        
        self.to_whom_btn.ids.txt_input.text = '@'
        #self.to_whom_btn.adaptive_height = True
        self.to_whom_btn.ids.txt_input.word_list = ['@'+k for k in self.app.keys if k != self.app.username]
        self.to_whom_btn.ids.txt_input.starting_no = 1
        # self.post_card.author_section_layout.add_widget(get_separator('1sp'))
        #self.post_card.author_section_layout.add_widget(self.to_whom_btn,3)

        # close for now
        # self.close_author_option()        
        # self.post_card.remove_widget(self.to_whom_btn)
        # self.to_whom_btn.height='0dp'
        # self.to_whom_btn.size_hint_y=None

        # remove content, add text input
        post.scroller.remove_widget(post.post_content)
        # self.post_card.author_section_layout.add_widget(get_separator('1dp'))
        # self.post_card.author_section_layout.add_widget(self.to_whom_layo,1)



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

        self.upload_button.font_size='12sp'
        self.post_button.font_size='12sp'
       

        self.post_button.md_bg_color=rgb(*COLOR_ACTIVE)
        self.upload_button.md_bg_color=rgb(*COLOR_ACTIVE)
        self.post_status.md_bg_color=rgb(*COLOR_CARD)
        
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

        #channels = [k[1:] for k,v in self.to_channels.items() if v]
        recipient = self.to_whom_btn.ids.txt_input.text
        self.log('RECIPIENT:',recipient)
        if not recipient: ##not hasattr(self,'recipient') or not self.recipient or self.app.username==self.recipient:
            self.log('no recipient was selected')
            # self.='No place was selected'
            return
        self.recipient = recipient
        channel = recipient

        # log('?????????????????'+self.media_uid)
        # if not hasattr(self,'img_id') and self.upload_button.selection:
        #     log('REUPLOADING')
        #     self.upload()

        async def do_post():
            file_id = self.img_id if hasattr(self,'img_id') else None
            file_ext = self.img_ext if hasattr(self,'img_ext') else None
            await self.app.post(content=content, channel = channel, file_id=file_id, file_ext=file_ext)
            import time
            self.close_dialog()
        
        # self.open_dialog('')
        #Thread(target=do_post).start()
        asyncio.create_task(do_post())        



def get_random_id():
    import uuid
    return uuid.uuid4().hex


class MessagePopup(MDDialog): pass