from kivy.uix.screenmanager import Screen,ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.theming import ThemeManager
from kivy.properties import ObjectProperty
from kivymd.uix.label import MDLabel

class MyLayout(BoxLayout):
    scr_mngr = ObjectProperty(None)

    def change_screen(self, screen, *args):
        self.scr_mngr.current = screen

class FeedScreen(Screen):
    def on_enter(self):
        with open('log.txt','a+') as of: of.write(str(dir(self)))
        print(dir(self))
        #self.add_widget(MDLabel(text='hello world!'))
    pass

class WelcomeScreen(Screen):
    pass

class PeopleScreen(Screen):
    pass

class EventsScreen(Screen):
    pass

class MessagesScreen(Screen):
    pass

class NotificationsScreen(Screen):
    pass


class MainApp(MDApp):
    # def build(self):
    #     self.theme_cls.primary_palette = "Red"  # "Purple", "Red"
    title = 'Gyre'

    def build(self):
        #self.theme_cls.primary_palette = "Green"  # "Purple", "Red"

        Builder.load_file('main.kv')
        # self.sm = ScreenManager()
        # self.sm.add_widget(BaseScreen(name='base'))
        # self.sm.add_widget(FeedScreen(name='feed'))

        # return self.sm



if __name__ == '__main__':
    App = MainApp()
    App.run()
