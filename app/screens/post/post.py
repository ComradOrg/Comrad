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

class InvisibleButton(Button):
    pass


def on_touch_down(self, touch):
    '''Receive a touch down event.
    :Parameters:
        `touch`: :class:`~kivy.input.motionevent.MotionEvent` class
            Touch received. The touch is in parent coordinates. See
            :mod:`~kivy.uix.relativelayout` for a discussion on
            coordinate systems.
    :Returns: bool
        If True, the dispatching of the touch event will stop.
        If False, the event will continue to be dispatched to the rest
        of the widget tree.
    '''
    if self.disabled and self.collide_point(*touch.pos):
        return True
    for child in self.children[:]:
        if child.dispatch('on_touch_down', touch):
            return True



class AuthorDialog(MDDialog): pass
    # def on_touch_down(self, touch):
    #     for item in self.items:
    #         logg(item.text, item.disabled)

        
        # author=self.screen.post_card.author
        # recip=self.screen.post_card.recipient
        # self.screen.post_card.author_label.text=f'@{author}\n[size=14sp]to @{recip}[/size]'
        
        # for item in self.screen.post_card.author_dialog.items:
        #     item.disabled=True
        # self.disabled=False

        # if self.disabled and self.collide_point(*touch.pos):
        #     return True
        # for child in self.children[:]:
        #     if child.dispatch('on_touch_down', touch):
        #         return True


from kivymd.uix.list import OneLineAvatarListItem,OneLineListItem
class Item(OneLineListItem):
    divider = None
    source = StringProperty()

    def on_release(self):
        raise Exception(self.text+'!')

    def change_title(self,new_recip):
        post=self.screen.post_card
        author=post.author
        post.recipient=recip=new_recip[1:]
        # raise Exception(recip+'???')
        newtitle=f'@{author}\n[size=14sp]to @{recip}!!![/size]'
        self.screen.post_card.author_label.text=newtitle
        

class AddresseeButton(MDRectangleFlatButton):
    pass
    def on_release(self):
        raise Exception(self.text+'!!!!!!!')

class PostScreen(ProtectedScreen): 
    post_id = ObjectProperty()


    def on_pre_enter(self):
        super().on_pre_enter()
        self.to_channels = {}
        
        # clear
        if hasattr(self,'post_status'): self.remove_widget(self.post_status)
        if hasattr(self,'post_textfield'): self.post_textfield.text=''

        post_json = {'author':self.app.username, 'timestamp':time.time()}
        key=list(self.app.keys.keys())[0]
        post_json['to_name']=key
        
        self.post_card = post = PostCard(post_json)
        self.post_card.add_widget(get_separator('15sp'),1)
        self.post_card.add_widget(get_separator('15sp'),1)
        self.post_textfield = post_TextField = AddPostTextField()
        post_TextField.line_color_focus=rgb(*COLOR_TEXT)
        post_TextField.line_color_normal=rgb(*COLOR_TEXT)
        post_TextField.current_hint_text_color=rgb(*COLOR_TEXT)
        post_TextField.font_name='assets/overpass-mono-regular.otf'
        post_TextField.hint_text='word?'

        # add recipient changer dialog widget
        
        self.to_whom_btn = InvisibleButton()
        self.to_whom_btn.background_color=0,0,0,0
        # self.post_card.author_section_layout.remove_widget()
        
        # self.to_whom_btn.add_widget(self.post_card.author_label)
        # self.post_card.author_section_layout.add_widget(self.to_whom_btn)

        # self.post_card.author_label.to_changeable=True
        # self.author_dialog_items = []
        # for key in self.app.keys:
        #     if key==self.app.username: continue
        #     item = Item(text="@"+key), source="assets/avatar.jpg")
        #     item.screen = self
        #     self.author_dialog_items += [item]

        buttons = [AddresseeButton(text=key) for key in self.app.keys if key!=self.app.username]
        for button in buttons:
            button.font_name='assets/font.otf'
            button.font_size='12sp'
            button.size_hint=(None,None)
            button.text_color=rgb(*COLOR_TEXT)
            # button.md_bg_color=1,1,0,1
        
        dial = self.post_card.author_dialog = MDDialog(
                title="to @whom",
                type="confirmation"
            )
        dial.cols=1
        dial.size_hint=(None,None)
        layo=MDBoxLayout()
        layo.font_size='12sp'
        # layo.md_bg_color=1,1,0,1
        layo.cols=1
        layo.orientation='vertical'
        layo.size_hint=(1,None)
        layo.adaptive_height=True

        dial.ids.container.add_widget(layo)
        dial.ids.container.size_hint=(1,None)
        dial.ids.container.height=layo.minimum_height
        for button in buttons:
            layo.add_widget(button)
        dial.height = layo.height
        self.post_card.author_dialog.pos_hint={'center_x':0.5}
        self.post_card.author_dialog.width='300sp'
        self.post_card.author_dialog.size_hint=(None,None)
        self.post_card.author_dialog.screen = self
        self.post_card.author_dialog.post_card = self.post_card


        
        # remove content, add text input
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

        channels = [k[1:] for k,v in self.to_channels.items() if v]
        if not channels:
            self.log('no place was selected')
            # self.='No place was selected'
            return

        # log('?????????????????'+self.media_uid)
        # if not hasattr(self,'img_id') and self.upload_button.selection:
        #     log('REUPLOADING')
        #     self.upload()

        async def do_post():
            file_id = self.img_id if hasattr(self,'img_id') else None
            file_ext = self.img_ext if hasattr(self,'img_ext') else None
            await self.app.post(content=content, channels = channels, file_id=file_id, file_ext=file_ext)
            import time
            self.close_dialog()
        
        self.open_dialog('posting')
        #Thread(target=do_post).start()
        asyncio.create_task(do_post())        



def get_random_id():
    import uuid
    return uuid.uuid4().hex