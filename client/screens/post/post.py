from screens.base import ProtectedScreen
from plyer import filechooser
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton
from kivy.properties import ListProperty,ObjectProperty
from kivy.app import App
from main import log
from screens.feed.feed import *
import os


class FileChoose(MDRectangleFlatButton):
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


class AddPostScreen(ProtectedScreen): 
    post_id = ObjectProperty()
    pass

class ViewPostScreen(ProtectedScreen): 
    post_id = ObjectProperty()

    def on_pre_enter(self):
        for child in self.children:
            log('child: '+str(child))
            self.remove_widget(child)
        
        post = self.app.get_post(self.root.post_id)
        log(post)
        img_src=os.path.join('cache','img',post['img_src']) if post['img_src'] else ''
        kwargs = dict(author='Marx Zuckerberg',
            title='',
            img_src=img_src,
            content=post['content'])
        log(kwargs)
        post = PostCard(**kwargs)
        
        print(post)
        self.add_widget(post)

    def on_enter(self):
        pass
        
    
    pass
