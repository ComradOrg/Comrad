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

class ProtectedScreen(BaseScreen):
    def on_pre_enter(self):
        async def guard():
            keys=await self.app.get_keys()
            if not self.channel in keys:
                self.root.change_screen('login')
                return
        asyncio.create_task(guard())