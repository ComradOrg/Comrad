from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.app import App



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

class ProtectedScreen(BaseScreen):
    def on_pre_enter(self):
        if not self.channel in self.app.keys:
            return
