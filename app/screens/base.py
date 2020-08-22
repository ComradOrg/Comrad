from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.app import App
import asyncio



### Layout

### Base screens
class BaseScreen(MDScreen):
    @property
    def root(self):
        return self.app.root

    @property
    def app(self):
        return App.get_running_app()

    def log(self,*x):
        return self.app.log(*x)

    @property
    def channel(self):
        return self.app.channel

    def open_dialog(self,msg):
        from screens.post.post import MessagePopup,ProgressPopup
        if not hasattr(self,'dialog') or not self.dialog:
            self.dialog = ProgressPopup()
        self.dialog.ids.progress_label.text=msg
        self.dialog.open()

    def open_msg_dialog(self,msg):
        from screens.post.post import MessagePopup,ProgressPopup
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


class ProtectedScreen(BaseScreen): pass
    # def on_pre_enter(self):
    #     if not self.channel in self.app.api.keys:
    #         self.root.change_screen('login')
    #         return
        