from screens.base import ProtectedScreen
from plyer import filechooser
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton
from kivy.properties import ListProperty,ObjectProperty
from kivy.app import App
from main import log
from screens.feed.feed import *



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

    def on_enter(self):
        ln='woops'
        
        post = PostCard(
            author='Marx Zuckerberg',
            title='',
            img_src='avatar.jpg',
            content=ln.strip())
        print(post)
        self.add_widget(post)
        
    
    pass
