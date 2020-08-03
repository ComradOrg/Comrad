from kivy.uix.screenmanager import Screen,ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.lang import Builder



class BaseScreen(Screen):
    pass

class FeedScreen(BaseScreen):
    pass





class MainApp(MDApp):
    # def build(self):
    #     self.theme_cls.primary_palette = "Red"  # "Purple", "Red"

    def build(self):
        Builder.load_file('main.kv')
        self.sm = ScreenManager()
        self.sm.add_widget(BaseScreen(name='base'))
        self.sm.add_widget(FeedScreen(name='feed'))

        return self.sm

    def go(self,x):
        self.sm.current=x



if __name__ == '__main__':
    App = MainApp()
    App.run()
