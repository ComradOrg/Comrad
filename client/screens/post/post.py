from screens.base import ProtectedScreen
from plyer import filechooser
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton
from kivy.properties import ListProperty
from kivy.app import App



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


class AddPostScreen(ProtectedScreen): pass

class ViewPostScreen(ProtectedScreen): pass
