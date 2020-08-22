from kivy.animation import Animation
from kivy.lang import Builder
from kivy.metrics import dp
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
from main import COLOR_TEXT,rgb,COLOR_ICON,COLOR_ACCENT

Builder.load_string(
    """
#:import DEVICE_TYPE kivymd.material_resources.DEVICE_TYPE
#:import COLOR_TEXT main.COLOR_TEXT
#:import COLOR_ICON main.COLOR_ICON
#:import rgb main.rgb

<MyChooseChip>
    adaptive_height: True
    spacing: "5dp"


<MyChip>
    size_hint: None,  None
    height: "26dp"
    padding: 0, 0, "5dp", 0
    width:
        self.minimum_width - (dp(10) if DEVICE_TYPE == "desktop" else dp(20)) \
        if root.icon != 'checkbox-blank-circle' else self.minimum_width
    theme_text_color: 'Custom'
    text_color:rgb(*COLOR_TEXT)

    # canvas:
    #     Color:
    #         rgba: root.color
    #     RoundedRectangle:
    #         pos: self.pos
    #         size: self.size
    #         radius: [root.radius]


    

    MDBoxLayout:
        id: box_check
        adaptive_size: True
        pos_hint: {'center_y': .5}

    MDBoxLayout:
        adaptive_width: True
        padding: dp(0)

        MDIconButton:
            id: icon
            icon: root.icon
            size_hint_y: None
            height: "20dp"
            pos_hint: {"center_y": .5}
            user_font_size: "20dp"
            disabled: True
            md_bg_color_disabled: 0, 0, 0, 0
            theme_text_color: "Custom"
            text_color: rgb(*COLOR_TEXT)

        Label:
            id: label
            text: root.label
            size_hint_x: None
            width: self.texture_size[0]
            color: root.text_color if root.text_color else (root.theme_cls.text_color)
            font_name: "assets/font.otf"
            font_size: "18sp"
    


"""

)

def get_separator(height,width=None,debug=False):
    from kivymd.uix.boxlayout import MDBoxLayout
    x=MDBoxLayout(height=height,size_hint=(None,None))
    # if debug: x.md_bg_color=(1,1,0,1)
    if width: x.width=width
    return x


class MyChip(BoxLayout, ThemableBehavior):
    label = StringProperty()
    """Chip text.

    :attr:`label` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    icon = StringProperty("checkbox-blank-circle")
    """Chip icon.

    :attr:`icon` is an :class:`~kivy.properties.StringProperty`
    and defaults to `'checkbox-blank-circle'`.
    """

    color = ListProperty()
    """Chip color in ``rgba`` format.

    :attr:`color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    text_color = ListProperty()
    """Chip's text color in ``rgba`` format.

    :attr:`text_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    check = BooleanProperty(False)
    """
    If True, a checkmark is added to the left when touch to the chip.

    :attr:`check` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    callback = ObjectProperty()
    """Custom method.

    :attr:`callback` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    radius = NumericProperty("12dp")
    """Corner radius values.

    :attr:`radius` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `'12dp'`.
    """

    selected_chip_color = ListProperty()
    """The color of the chip that is currently selected in ``rgba`` format.

    :attr:`selected_chip_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.color:
            self.color = rgb(*COLOR_TEXT) #self.theme_cls.primary_color

    def on_icon(self, instance, value):
        if value == "":
            self.icon = "checkbox-blank-circle"
            self.remove_widget(self.ids.icon)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            md_choose_chip = self.parent
            if self.selected_chip_color:
                Animation(
                    color=self.theme_cls.primary_dark
                    if not self.selected_chip_color
                    else self.selected_chip_color,
                    d=0.3,
                ).start(self)
            if issubclass(md_choose_chip.__class__, MDChooseChip):
                for chip in md_choose_chip.children:
                    if chip is not self:
                        chip.color = self.theme_cls.primary_color
            if self.check:
                if not len(self.ids.box_check.children):
                    self.ids.box_check.add_widget(
                        MDIconButton(
                            icon="check",
                            size_hint_y=None,
                            height=dp(20),
                            disabled=True,
                            user_font_size=dp(20),
                            pos_hint={"center_y": 0.5},
                        )
                    )
                else:
                    check = self.ids.box_check.children[0]
                    self.ids.box_check.remove_widget(check)
            if self.callback:
                self.callback(self, self.label)

class MDChooseChip(MDStackLayout):
    def add_widget(self, widget, index=0, canvas=None):
        if isinstance(widget, MyChip):
            return super().add_widget(widget)













#### DROPDOWN
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
           
Builder.load_string('''
<Body>:
    canvas:
        Color:
            rgba:(1, 1, 1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
            

<DropDownWidget>:
    canvas:
        Color:
            rgba:(1, 1, 1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
            
    orientation: 'vertical'
    spacing: 2
    size_hint:None,None
    # width:self.minimum_width
    txt_input: txt_input
    rv: rv

    MyTextInput:
        id: txt_input
        size_hint_y: None
        height: 50
    RV:
        id: rv
    
<MyTextInput>:
    readonly: False
    multiline: False
    

<SelectableLabel>:
    # Draw a background to indicate selection
    color: 0,0,0,1
    
    canvas.before:
        Color:
            rgba: (0, 0, 1, .5) if self.selected else (1, 1, 1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
<RV>:
    canvas:
        Color:
            rgba: 0,0,0,.2

        Line:
            rectangle: self.x +1 , self.y, self.width - 2, self.height -2
         
    bar_width: 10
    scroll_type:['bars']
    viewclass: 'SelectableLabel'
    SelectableRecycleBoxLayout:
        default_size: None, dp(20)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        size_hint:None,None
        multiselect: False
        ''')

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        # raise Exception(str([is_selected, rv.data[index]]))
        if is_selected:
            # raise Exception(str([is_selected, rv.data[index]]))
            newval=rv.data[index]['text']
            try:
                pcard=self.parent.parent.parent.parent.parent
            except AttributeError:
                return
            pcard.recipient=newval[1:]
            alabel=pcard.author_label
            alabel.text=f'@{pcard.author}\n[size=14sp]to @{pcard.recipient}[/size]'
            pcard.author_section_layout.remove_widget(pcard.parent.to_whom_btn)
            # pcard.author_section_layout.remove_widget(pcard.author_section_layout.children[2])
            # pcard.remove_widget(pcard.parent.to_whom_btn)
            # pcard.remove_widget(self.parent.parent.parent)
            #raise Exception(type())
            # self.parent.parent.parent.children[1].text = rv.data[index]['text']
            #raise Exception(type(=self.te))
            #print("selection changed to {0}".format(rv.data[index]))

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)

class DropDownWidget(BoxLayout):
    txt_input = ObjectProperty()
    rv = ObjectProperty()
    
class MyTextInput(TextInput):
    txt_input = ObjectProperty()
    flt_list = ObjectProperty()
    word_list = ListProperty()
    #this is the variable storing the number to which the look-up will start
    starting_no = NumericProperty(3)
    suggestion_text = ''

    def __init__(self, **kwargs):
        super(MyTextInput, self).__init__(**kwargs)
        
    def on_text(self, instance, value):
        #find all the occurrence of the word
        self.parent.ids.rv.data = []
        matches = [self.word_list[i] for i in range(len(self.word_list)) if self.word_list[i][:self.starting_no] == value[:self.starting_no]]
        #display the data in the recycleview
        display_data = []
        for i in matches:
            display_data.append({'text':i})
        self.parent.ids.rv.data = display_data
        #ensure the size is okay
        if len(matches) <= 10:
            self.parent.height = (50 + (len(matches)*20))
        else:
            self.parent.height = 240
        
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if self.suggestion_text and keycode[1] == 'tab':
            self.insert_text(self.suggestion_text + ' ')
            return True
        return super(MyTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)

class Body(FloatLayout):
    def __init__(self, **kwargs):
        super(Body, self).__init__(**kwargs)
        widget_1 = DropDownWidget(pos_hint = {'center_x':.5,'center_y':.5}, \
                               size_hint = (None, None), size = (600, 60))
        widget_1.ids.txt_input.word_list = ['how to use python', 'how to use kivy', 'how to ...']
        widget_1.ids.txt_input.starting_no = 3
        self.add_widget(widget_1)
 
