from kivy.uix.screenmanager import Screen,ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.theming import ThemeManager
from kivy.properties import ObjectProperty,ListProperty
import time
from collections import OrderedDict
from functools import partial
from kivy.uix.screenmanager import NoTransition
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget

root = None
app = None

def log(x):
    with open('log.txt','a+') as of:
        of.write(str(x)+'\n')

class MyLayout(BoxLayout):
    scr_mngr = ObjectProperty(None)
    #orientation = 'vertical'

    def change_screen(self, screen, *args):
        self.scr_mngr.current = screen

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orientation='vertical'
        self.add_widget(MyToolbar())

class MyIconButton(MDIconButton):
    kwargs = dict(theme_text_color='Custom',text_color=(1,0,0,1),pos_hint = {'center_y': 0.5})
    def __init__(self, screen_name, *args, **kwargs):
        kwargs = dict(list(self.kwargs.items()) + list(kwargs.items()))
        kwargs['on_release'] = lambda x: app.change_screen(screen_name)
        super().__init__(*args, **kwargs)

class MyLabel(MDLabel):
    kwargs = dict(theme_text_color='Custom',text_color=(1,0,0,1), pos_hint = {'center_y': 0.5})
    def __init__(self, *args, **kwargs):
        kwargs = dict(list(self.kwargs.items()) + list(kwargs.items()))
        super().__init__(*args, **kwargs) 

class MyToolbar(MDToolbar):

    def change_screen(self,x, *args, **kwargs):
        app.change_screen(x)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.id='toolbar'
    #     self.title='Gyre'
    #     self.pos_hint = {'center_x': .5, 'center_y': 0.95}
    #     self.md_bg_color = (0,0,0,1)
    #     # self.ids['left_actions'] = left = Widget()
    #     # self.ids['right_actions'] = right = Widget()
    #     # self.specific_text_color = (1,0,0,1)

        
    #     # Add icons

    #     self.add_widget(MyIconButton('feed', icon='radio-tower'))
    #     self.add_widget(MyIconButton('people', icon='account-group'))
    #     self.add_widget(MyIconButton('events', icon='calendar'))
    #     self.add_widget(MyIconButton('messages', icon='message-processing-outline'))
    #     self.add_widget(MyIconButton('notifications', icon='bell-outline'))
        

    # def button_notif(self):
    #     return MyIconButton('notifications', icon='bell-outline')


class BaseScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #self.add_widget(MDLabel(text='Turning and turning in the widening gyre   \nThe falcon cannot hear the falconer;\nThings fall apart; the centre cannot hold;\nMere anarchy is loosed upon the world,\nThe blood-dimmed tide is loosed, and everywhere   \nThe ceremony of innocence is drowned;\nThe best lack all conviction, while the worst   \nAre full of passionate intensity.\n\nSurely some revelation is at hand;\nSurely the Second Coming is at hand.   \nThe Second Coming! Hardly are those words out   \nWhen a vast image out of Spiritus Mundi\nTroubles my sight: somewhere in sands of the desert   \nA shape with lion body and the head of a man,   \nA gaze blank and pitiless as the sun,   \nIs moving its slow thighs, while all about it   \nReel shadows of the indignant desert birds.   \nThe darkness drops again; but now I know   \nThat twenty centuries of stony sleep\nWere vexed to nightmare by a rocking cradle,   \nAnd what rough beast, its hour come round at last,   \nSlouches towards Bethlehem to be born?'))
    

class FeedScreen(MDScreen):
    pass

class WelcomeScreen(MDScreen):
    id='welcome'

    #def on_enter(self, *args, **kwargs):
    #    super().on_enter()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.add_widget(
        #     MDFillRoundFlatButton(
        #         text="Hello, World",
        #         pos_hint={"center_x": 0.5, "center_y": 0.5},
        #     )
        # )
        self.add_widget(
            MyLabel(
                text='Turning and turning in the widening gyre   \nThe falcon cannot hear the falconer;\nThings fall apart; the centre cannot hold;\nMere anarchy is loosed upon the world,\nThe blood-dimmed tide is loosed, and everywhere   \nThe ceremony of innocence is drowned;\nThe best lack all conviction, while the worst   \nAre full of passionate intensity.\n\nSurely some revelation is at hand;\nSurely the Second Coming is at hand.   \nThe Second Coming! Hardly are those words out   \nWhen a vast image out of Spiritus Mundi\nTroubles my sight: somewhere in sands of the desert   \nA shape with lion body and the head of a man,   \nA gaze blank and pitiless as the sun,   \nIs moving its slow thighs, while all about it   \nReel shadows of the indignant desert birds.   \nThe darkness drops again; but now I know   \nThat twenty centuries of stony sleep\nWere vexed to nightmare by a rocking cradle,   \nAnd what rough beast, its hour come round at last,   \nSlouches towards Bethlehem to be born?',
                halign='center'
            )
        )

    pass

class PeopleScreen(MDScreen):
    pass

class EventsScreen(MDScreen):
    pass

class MessagesScreen(MDScreen):
    pass

class NotificationsScreen(MDScreen):
    pass


 
class MainApp(MDApp):
    # def build(self):
    #     self.theme_cls.primary_palette = "Red"  # "Purple", "Red"
    title = 'Gyre'

    def build1(self):
        global root,app
        root = MyLayout()
        app = self

        

        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette='Red'
        self.theme_cls.theme_style='Dark'
        
        self.screens = OrderedDict()
        self.screens['welcome']=WelcomeScreen(name='welcome')
        self.screens['feed']=FeedScreen(name='feed')
        self.screens['people']=PeopleScreen(name='people')
        self.screens['events']=EventsScreen(name='events')
        self.screens['messages']=MessagesScreen(name='messages')
        self.screens['notifications']=NotificationsScreen(name='notifications')


        self.sm = ScreenManager()
        for screen in self.screens.values():
            self.sm.add_widget(screen)
        
        root.add_widget(self.sm)

        return root

    def build(self):
        global root,app
        app = self
        root = Builder.load_file('main1.kv')
        return root

    def change_screen(self,x):
        #log('testing2')
        self.sm.switch_to(self.screens[x], transition=NoTransition())



if __name__ == '__main__':
    App = MainApp()
    App.run()
