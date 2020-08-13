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


Builder.load_string(
    """
#:import DEVICE_TYPE kivymd.material_resources.DEVICE_TYPE


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
    text_color:1,0,0,1

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
            text_color: 1,0,0,1

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
            self.color = (1,0,0,1) #self.theme_cls.primary_color

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
