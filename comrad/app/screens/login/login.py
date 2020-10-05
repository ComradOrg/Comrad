import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from comrad import *
from screens.base import *
from kivymd.uix.boxlayout import *
from kivymd.uix.textfield import *
from kivymd.uix.button import *
from kivymd.uix.label import *
from kivymd.uix.card import *
from kivy.uix.label import *
from kivymd.uix.dialog import *
from main import *
from misc import *
from kivy.app import *

import logging
logger = logging.getLogger(__name__)

import sys

from kivy.animation import Animation
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from kivymd.font_definitions import theme_font_styles
from kivymd.material_resources import DEVICE_TYPE
from kivymd.theming import ThemableBehavior
from kivymd.uix.label import MDIcon








class LoginBoxLayout(MDBoxLayout): pass
class LoginButtonLayout(MDBoxLayout): pass
# # class UsernameField(MDTextField): pass
#     def __init__(self,*x,**y):
#         super().__init__(*x,**y)
#         self.focus=True
#     def on_text_validate(self):
#         reg_button=self.parent.parent.parent.register_button
#         reg_button.enter()



class UsernameField(ThemableBehavior, TextInput):
    helper_text = StringProperty("This field is required")
    """
    Text for ``helper_text`` mode.
    :attr:`helper_text` is an :class:`~kivy.properties.StringProperty`
    and defaults to `'This field is required'`.
    """

    helper_text_mode = OptionProperty(
        "none", options=["none", "on_error", "persistent", "on_focus"]
    )
    """
    Helper text mode. Available options are: `'on_error'`, `'persistent'`,
    `'on_focus'`.
    :attr:`helper_text_mode` is an :class:`~kivy.properties.OptionProperty`
    and defaults to `'none'`.
    """

    max_text_length = NumericProperty(None)
    """
    Maximum allowed value of characters in a text field.
    :attr:`max_text_length` is an :class:`~kivy.properties.NumericProperty`
    and defaults to `None`.
    """

    required = BooleanProperty(False)
    """
    Required text. If True then the text field requires text.
    :attr:`required` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    color_mode = OptionProperty(
        "primary", options=["primary", "accent", "custom"]
    )
    """
    Color text mode. Available options are: `'primary'`, `'accent'`,
    `'custom'`.
    :attr:`color_mode` is an :class:`~kivy.properties.OptionProperty`
    and defaults to `'primary'`.
    """

    mode = OptionProperty("line", options=["rectangle", "fill"])
    """
    Text field mode. Available options are: `'line'`, `'rectangle'`, `'fill'`.
    :attr:`mode` is an :class:`~kivy.properties.OptionProperty`
    and defaults to `'line'`.
    """

    line_color_normal = ListProperty()
    """
    Line color normal in ``rgba`` format.
    :attr:`line_color_normal` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    line_color_focus = ListProperty()
    """
    Line color focus in ``rgba`` format.
    :attr:`line_color_focus` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    error_color = ListProperty()
    """
    Error color in ``rgba`` format for ``required = True``.
    :attr:`error_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    fill_color = ListProperty((0, 0, 0, 0))
    """
    The background color of the fill in rgba format when the ``mode`` parameter
    is "fill".
    :attr:`fill_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `(0, 0, 0, 0)`.
    """

    active_line = BooleanProperty(True)
    """
    Show active line or not.
    :attr:`active_line` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `True`.
    """

    error = BooleanProperty(False)
    """
    If True, then the text field goes into ``error`` mode.
    :attr:`error` is an :class:`~kivy.properties.BooleanProperty`
    and defaults to `False`.
    """

    current_hint_text_color = ListProperty()
    """
    ``hint_text`` text color.
    :attr:`current_hint_text_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    icon_right = StringProperty()
    """Right icon.
    :attr:`icon_right` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    icon_right_color = ListProperty((0, 0, 0, 1))
    """Color of right icon in ``rgba`` format.
    :attr:`icon_right_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `(0, 0, 0, 1)`.
    """

    _text_len_error = BooleanProperty(False)
    _hint_lbl_font_size = NumericProperty("16sp")
    _line_blank_space_right_point = NumericProperty(0)
    _line_blank_space_left_point = NumericProperty(0)
    _hint_y = NumericProperty("38dp")
    _line_width = NumericProperty(0)
    _current_line_color = ListProperty((0, 0, 0, 0))
    _current_error_color = ListProperty((0, 0, 0, 0))
    _current_hint_text_color = ListProperty((0, 0, 0, 0))
    _current_right_lbl_color = ListProperty((0, 0, 0, 0))

    _msg_lbl = None
    _right_msg_lbl = None
    _hint_lbl = None
    _lbl_icon_right = None

    def __init__(self, **kwargs):
        self.set_objects_labels()
        super().__init__(**kwargs)
        # Sets default colors.
        self.line_color_normal = self.theme_cls.divider_color
        self.line_color_focus = self.theme_cls.primary_color
        self.error_color = self.theme_cls.error_color
        self._current_hint_text_color = self.theme_cls.disabled_hint_text_color
        self._current_line_color = self.theme_cls.primary_color

        self.bind(
            helper_text=self._set_msg,
            hint_text=self._set_hint,
            _hint_lbl_font_size=self._hint_lbl.setter("font_size"),
            helper_text_mode=self._set_message_mode,
            max_text_length=self._set_max_text_length,
            text=self.on_text,
        )
        self.theme_cls.bind(
            primary_color=self._update_primary_color,
            theme_style=self._update_theme_style,
            accent_color=self._update_accent_color,
        )
        self.has_had_text = False
        self.focus=True

    def set_objects_labels(self):
        """Creates labels objects for the parameters
        `helper_text`,`hint_text`, etc."""

        # Label object for `helper_text` parameter.
        self._msg_lbl = TextfieldLabel(
            font_style="Caption",
            halign="left",
            valign="middle",
            text=self.helper_text,
            field=self,
        )
        # Label object for `max_text_length` parameter.
        self._right_msg_lbl = TextfieldLabel(
            font_style="Caption",
            halign="right",
            valign="middle",
            text="",
            field=self,
        )
        # Label object for `hint_text` parameter.
        self._hint_lbl = TextfieldLabel(
            font_style="Subtitle1", halign="left", valign="middle", field=self
        )
        # MDIcon object for the icon on the right.
        self._lbl_icon_right = MDIcon(theme_text_color="Custom")

    def on_icon_right(self, instance, value):
        self._lbl_icon_right.icon = value

    def on_icon_right_color(self, instance, value):
        self._lbl_icon_right.text_color = value

    def on_width(self, instance, width):
        """Called when the application window is resized."""

        if (
            any((self.focus, self.error, self._text_len_error))
            and instance is not None
        ):
            # Bottom line width when active focus.
            self._line_width = width
        self._msg_lbl.width = self.width
        self._right_msg_lbl.width = self.width

    def on_focus(self, *args):
        disabled_hint_text_color = self.theme_cls.disabled_hint_text_color
        Animation.cancel_all(
            self, "_line_width", "_hint_y", "_hint_lbl_font_size"
        )
        self._set_text_len_error()

        if self.focus:
            self._line_blank_space_right_point = (
                self._get_line_blank_space_right_point()
            )
            _fill_color = self.fill_color
            _fill_color[3] = self.fill_color[3] - 0.1
            if not self._get_has_error():
                Animation(
                    _line_blank_space_right_point=self._line_blank_space_right_point,
                    _line_blank_space_left_point=self._hint_lbl.x - dp(5),
                    _current_hint_text_color=self.line_color_focus,
                    fill_color=_fill_color,
                    duration=0.2,
                    t="out_quad",
                ).start(self)
            self.has_had_text = True
            Animation.cancel_all(
                self, "_line_width", "_hint_y", "_hint_lbl_font_size"
            )
            if not self.text:
                self._anim_lbl_font_size(dp(14), sp(12))
            Animation(_line_width=self.width, duration=0.2, t="out_quad").start(
                self
            )
            if self._get_has_error():
                self._anim_current_error_color(self.error_color)
                if self.helper_text_mode == "on_error" and (
                    self.error or self._text_len_error
                ):
                    self._anim_current_error_color(self.error_color)
                elif (
                    self.helper_text_mode == "on_error"
                    and not self.error
                    and not self._text_len_error
                ):
                    self._anim_current_error_color((0, 0, 0, 0))
                elif self.helper_text_mode in ("persistent", "on_focus"):
                    self._anim_current_error_color(disabled_hint_text_color)
            else:
                self._anim_current_right_lbl_color(disabled_hint_text_color)
                Animation(
                    duration=0.2, _current_hint_text_color=self.line_color_focus
                ).start(self)
                if self.helper_text_mode == "on_error":
                    self._anim_current_error_color((0, 0, 0, 0))
                if self.helper_text_mode in ("persistent", "on_focus"):
                    self._anim_current_error_color(disabled_hint_text_color)
        else:
            _fill_color = self.fill_color
            _fill_color[3] = self.fill_color[3] + 0.1
            Animation(fill_color=_fill_color, duration=0.2, t="out_quad").start(
                self
            )
            if not self.text:
                self._anim_lbl_font_size(dp(38), sp(16))
                Animation(
                    _line_blank_space_right_point=0,
                    _line_blank_space_left_point=0,
                    duration=0.2,
                    t="out_quad",
                ).start(self)
            if self._get_has_error():
                self._anim_get_has_error_color(self.error_color)
                if self.helper_text_mode == "on_error" and (
                    self.error or self._text_len_error
                ):
                    self._anim_current_error_color(self.error_color)
                elif (
                    self.helper_text_mode == "on_error"
                    and not self.error
                    and not self._text_len_error
                ):
                    self._anim_current_error_color((0, 0, 0, 0))
                elif self.helper_text_mode == "persistent":
                    self._anim_current_error_color(disabled_hint_text_color)
                elif self.helper_text_mode == "on_focus":
                    self._anim_current_error_color((0, 0, 0, 0))
            else:
                Animation(duration=0.2, color=(1, 1, 1, 1)).start(
                    self._hint_lbl
                )
                self._anim_get_has_error_color()
                if self.helper_text_mode == "on_error":
                    self._anim_current_error_color((0, 0, 0, 0))
                elif self.helper_text_mode == "persistent":
                    self._anim_current_error_color(disabled_hint_text_color)
                elif self.helper_text_mode == "on_focus":
                    self._anim_current_error_color((0, 0, 0, 0))
                Animation(_line_width=0, duration=0.2, t="out_quad").start(self)

    def on_text(self, instance, text):
        if len(text) > 0:
            self.has_had_text = True
        if self.max_text_length is not None:
            self._right_msg_lbl.text = f"{len(text)}/{self.max_text_length}"
        self._set_text_len_error()
        if self.error or self._text_len_error:
            if self.focus:
                self._anim_current_line_color(self.error_color)
                if self.helper_text_mode == "on_error" and (
                    self.error or self._text_len_error
                ):
                    self._anim_current_error_color(self.error_color)
                if self._text_len_error:
                    self._anim_current_right_lbl_color(self.error_color)
        else:
            if self.focus:
                self._anim_current_right_lbl_color(
                    self.theme_cls.disabled_hint_text_color
                )
                self._anim_current_line_color(self.line_color_focus)
                if self.helper_text_mode == "on_error":
                    self._anim_current_error_color((0, 0, 0, 0))
        if len(self.text) != 0 and not self.focus:
            self._hint_y = dp(14)
            self._hint_lbl_font_size = sp(12)

    def on_text_validate(self):
        self.has_had_text = True
        self._set_text_len_error()

        # custom
        reg_button=self.parent.parent.parent.register_button
        reg_button.enter()

    def on_color_mode(self, instance, mode):
        if mode == "primary":
            self._update_primary_color()
        elif mode == "accent":
            self._update_accent_color()
        elif mode == "custom":
            self._update_colors(self.line_color_focus)

    def on_line_color_focus(self, *args):
        if self.color_mode == "custom":
            self._update_colors(self.line_color_focus)

    def on__hint_text(self, instance, value):
        pass

    def _anim_get_has_error_color(self, color=None):
        # https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/_get_has_error.png
        if not color:
            line_color = self.line_color_focus
            hint_text_color = self.theme_cls.disabled_hint_text_color
            right_lbl_color = (0, 0, 0, 0)
        else:
            line_color = color
            hint_text_color = color
            right_lbl_color = color
        Animation(
            duration=0.2,
            _current_line_color=line_color,
            _current_hint_text_color=hint_text_color,
            _current_right_lbl_color=right_lbl_color,
        ).start(self)

    def _anim_current_line_color(self, color):
        # https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/_anim_current_line_color.gif
        Animation(
            duration=0.2,
            _current_hint_text_color=color,
            _current_line_color=color,
        ).start(self)

    def _anim_lbl_font_size(self, hint_y, font_size):
        Animation(
            _hint_y=hint_y,
            _hint_lbl_font_size=font_size,
            duration=0.2,
            t="out_quad",
        ).start(self)

    def _anim_current_right_lbl_color(self, color, duration=0.2):
        # https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/_anim_current_right_lbl_color.png
        Animation(duration=duration, _current_right_lbl_color=color).start(self)

    def _anim_current_error_color(self, color, duration=0.2):
        # https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/_anim_current_error_color_to_disabled_color.gif
        # https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/_anim_current_error_color_to_fade.gif
        Animation(duration=duration, _current_error_color=color).start(self)

    def _update_colors(self, color):
        self.line_color_focus = color
        if not self.error and not self._text_len_error:
            self._current_line_color = color
            if self.focus:
                self._current_line_color = color

    def _update_accent_color(self, *args):
        if self.color_mode == "accent":
            self._update_colors(self.theme_cls.accent_color)

    def _update_primary_color(self, *args):
        if self.color_mode == "primary":
            self._update_colors(self.theme_cls.primary_color)

    def _update_theme_style(self, *args):
        self.line_color_normal = self.theme_cls.divider_color
        if not any([self.error, self._text_len_error]):
            if not self.focus:
                self._current_hint_text_color = (
                    self.theme_cls.disabled_hint_text_color
                )
                self._current_right_lbl_color = (
                    self.theme_cls.disabled_hint_text_color
                )
                if self.helper_text_mode == "persistent":
                    self._current_error_color = (
                        self.theme_cls.disabled_hint_text_color
                    )

    def _get_has_error(self):
        if self.error or all(
            [
                self.max_text_length is not None
                and len(self.text) > self.max_text_length
            ]
        ):
            has_error = True
        else:
            if all((self.required, len(self.text) == 0, self.has_had_text)):
                has_error = True
            else:
                has_error = False
        return has_error

    def _get_line_blank_space_right_point(self):
        # https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/_line_blank_space_right_point.png
        return (
            self._hint_lbl.texture_size[0]
            - self._hint_lbl.texture_size[0] / 100 * dp(18)
            if DEVICE_TYPE == "desktop"
            else dp(10)
        )

    def _get_max_text_length(self):
        """Returns the maximum number of characters that can be entered in a
        text field."""

        return (
            sys.maxsize
            if self.max_text_length is None
            else self.max_text_length
        )

    def _set_text_len_error(self):
        if len(self.text) > self._get_max_text_length() or all(
            (self.required, len(self.text) == 0, self.has_had_text)
        ):
            self._text_len_error = True
        else:
            self._text_len_error = False

    def _set_hint(self, instance, text):
        self._hint_lbl.text = text

    def _set_msg(self, instance, text):
        self._msg_lbl.text = text
        self.helper_text = text

    def _set_message_mode(self, instance, text):
        self.helper_text_mode = text
        if self.helper_text_mode == "persistent":
            self._anim_current_error_color(
                self.theme_cls.disabled_hint_text_color, 0.1
            )

    def _set_max_text_length(self, instance, length):
        self.max_text_length = length
        self._right_msg_lbl.text = f"{len(self.text)}/{length}"

    def _refresh_hint_text(self):
        pass



    
class PasswordField(MDTextField): pass
class LoginButton(MDRectangleFlatButton): pass
class RegisterButton(MDRectangleFlatButton,Logger):
    def enter(self):
        un=self.parent.parent.parent.username_field.text
        # pw=self.parent.parent.parent.password_field.text
        login_screen = self.parent.parent.parent

        time.sleep(0.1)
        asyncio.create_task(login_screen.boot(un))

        # logger.info('types',type(self.parent),type(self.parent.parent.parent))
        
        # app=App.get_running_app()
        # app.boot(un)
        # app.change_screen_from_uri(f'/inbox/{un}')
    
    pass
class LoginStatus(MDLabel): pass

class UsernameLayout(MDBoxLayout): pass
class UsernameLabel(MDLabel): pass
class WelcomeLabel(MDLabel): pass

class PasswordPopup(MDDialog): pass

class LoginScreen(BaseScreen): 
    #def on_pre_enter(self):
    #    global app
    #    if app.is_logged_in():
    #        app.root.change_screen('feed')
    def on_pre_enter(self):
        #log(self.ids)
        #log('hello?')
        super().on_pre_enter()
        self.dialog=None
        self.pass_added=False
        self.layout = LoginBoxLayout()
        self.label_title = WelcomeLabel()
        self.label_title.font_name='assets/font.otf'
        # self.label_title.font_size='20sp'
        self.label_title.bold=True
        self.label_title.markup=True
        self.label_title.color=rgb(*COLOR_TEXT)
        self.label_title.text='Welcome,'
        self.layout.add_widget(get_separator('20sp'))
        self.layout.add_widget(self.label_title)
        self.layout.add_widget(get_separator('30sp'))
        # self.layout.add_widget(MySeparator())
        

        self.layout_username = UsernameLayout()
        self.label_username = UsernameLabel(text="Comrad @")

        self.username_field = UsernameField()
        self.username_field.line_color_focus=rgb(*COLOR_TEXT)
        self.username_field.line_color_normal=rgb(*COLOR_TEXT)
        self.username_field.font_name='assets/font.otf'
        self.username_field.width='10dp'

        self.layout_username.add_widget(self.label_username)
        self.layout_username.add_widget(self.username_field)

        self.layout.add_widget(self.layout_username)
        #log(self.username_field)
        # self.username_field.text='hello????'

        # self.layout_password = UsernameLayout()
        # self.label_password = UsernameLabel(text='password:')

        # self.label_password.font_name='assets/font.otf'
        self.label_username.font_name='assets/font.otf'

        # self.password_field = PasswordField()
        # self.password_field.line_color_focus=rgb(*COLOR_TEXT)
        # self.password_field.line_color_normal=rgb(*COLOR_TEXT,a=0.25)
        # self.password_field.font_name='assets/font.otf'
        
        # self.layout_password.add_widget(self.label_password)
        # self.layout_password.add_widget(self.password_field)
        # self.layout.add_widget(self.layout_password)

        self.layout_buttons = LoginButtonLayout()
        self.layout.add_widget(get_separator('20sp'))
        self.layout.add_widget(self.layout_buttons)

        self.login_button = LoginButton()
        self.login_button.font_name='assets/font.otf'
        # self.layout_buttons.add_widget(self.login_button)

        self.register_button = RegisterButton()
        self.register_button.font_name='assets/font.otf'
        # self.register_button = 
        self.layout_buttons.add_widget(self.register_button)

        self.login_status = LoginStatus()
        self.login_status.font_name='assets/font.otf'
        
        self.layout.add_widget(self.login_status)

        self.label_title.font_size='24sp'
        # self.label_password.font_size='18sp'
        self.label_username.font_size='22sp'
        self.login_button.font_size='12sp'
        self.register_button.font_size='9sp'
        self.register_button.text='enter'
        self.username_field.font_size='24sp'
        self.label_username.padding_x=(10,20)
        # self.username_field.padding_x=(20,10)
        # self.username_field.padding_y=(25,0)
        self.username_field.pos_hint={'center_y':0.5}
        self.label_username.halign='right'
        


        ## add all
        self.add_widget(self.layout)
        #pass


    # def on_enter(self):
    #     un=self.app.get_username()
    #     if un: self.username_field.text = un

    def show_pass_opt(self):
        if not self.pass_added:
            self.layout.add_widget(self.layout_password,index=2)
            self.pass_added=True

    def show_pass_opt1(self,button_text='login'):
        if not self.dialog:
            self.dialog = PasswordPopup(
                title="password:",
                type="custom",
                content_cls=MDTextField(password=True),
                buttons=[
                    MDFlatButton(
                        text="login"
                    ),
                ],
            )
        self.dialog.open()

    def getpass_func(self,why_msg,passphrase=None):
        return self.password_field.text if not passphrase else passphrase
        
    async def boot(self,un,pw=None):
        # await self.stat('hello',img_src='/home/ryan/comrad/data/contacts/marxxx.png',comrad_name='Keymaker')

        # await self.app.get_input('hello?',get_pass=True,title='gimme your passwrdd')
        # await self.app.get_input('hello?',get_pass=False,title='gimme your fav color bitch')
        # return
        # self.remove_widget(self.layout)


        # from screens.map import MapWidget,default_places
        # map = MapWidget()
        # map.open()
        # map.add_point(*default_places['Cambridge'],desc='Cambridge')
        # map.draw()
        # await asyncio.sleep(1)
        # map.add_point(*default_places['San Francisco'],desc='San Francisco')
        # map.draw()
        # await asyncio.sleep(1)
        # map.add_point(*default_places['Reykjavik'],desc='Reykjavik')
        # map.draw()
        # await asyncio.sleep(1)
        # return

        # remove login layout for now
        self.remove_widget(self.layout)


        # return
        name=un
        from comrad.backend import Comrad

        
        commie = Comrad(un)
        self.log('KOMMIE!?!?',commie)
        self.log('wtf',PATH_CRYPT_CA_KEYS)

        logger.info(f'booted commie: {commie}')
        if commie.exists_locally_as_account():
            # pw='marx' # @HACK FOR NOW
            pw=await self.app.get_input('Welcome back.',get_pass=True)
            commie.keychain(passphrase=pw)
            logger.info(f'updated keychain: {dict_format(commie.keychain())}')
            logger.info(f'is account')
            # self.login_status.text='You should be able to log into this account.'
            if commie.privkey:
                logger.info(f'passkey login succeeded')
                
                # get new data
                # res = await commie.get_updates()
                # if not res.get('res_login',{}).get('success'):
                #     return {'success':False,'res_refresh':refresh}
                 
                # otherwise, ok
                self.login_status.text=f'Welcome back, Comrad @{un}'
                self.app.is_logged_in=True
                self.app.username=commie.name
                self.app.comrad=commie
                self.root.change_screen('feed')
            else:
                logger.info(f'passkey login failed')
                self.login_status.text='Login failed...'
    

        #   self.layout.add_widget(self.layout_password)
        elif commie.exists_locally_as_contact():
            await self.app.stat('This is a contact of yours')
            self.login_status.text='Comrad exists as a contact of yours.'
            # self.app.change_screen('feed')
            self.app.change_screen('login')
        else:
            # await self.app.stat('Account does not exist on hardware, maybe not on server. Try to register?')
            # self.login_status.text='Comrad not known on this device. Registering...'
            
            ### REGISTER
            self.remove_widget(self.layout)
            res = await self.register(un)
            
            if commie.privkey:
                self.login_status.text='Registered'
                self.app.is_logged_in=True
                self.app.username=commie.name
                self.app.comrad=commie
                self.remove_widget(self.layout)
                self.app.change_screen('feed')
            else:
                self.login_status.text = 'Sign up failed...'
                self.app.change_screen('login')
        return 1

    
    async def register(self,name):
        async def logfunc(*x,**y):
            if not 'comrad_name' in y: y['comrad_name']='Keymaker'
            await self.app.stat(*x,**y)
        
        commie = Comrad(name)
        self.app.comrad = commie

        # already have it?
        if commie.exists_locally_as_account():
            return {'success':False, 'status':'You have already created this account.'}        
        if commie.exists_locally_as_contact():
            return {'success':False, 'status':'This is already a contact of yours'}
            
        # 
        await logfunc(f'Hello, this is Comrad @{name}. I would like to join the socialist network.',pause=True,comrad_name=name)
        
        await logfunc(f'Welcome, Comrad @{name}. To help us communicate safely, I have cut for you a matching pair of encryption keys.',pause=True,clear=True,comrad_name='Keymaker')


        # ## 2) Make pub public/private keys
        from comrad.backend.keymaker import ComradAsymmetricKey
        from comrad.cli.artcode import ART_KEY_PAIR
        keypair = ComradAsymmetricKey()
        logger.info('cut keypair!')
        pubkey,privkey = keypair.pubkey_obj,keypair.privkey_obj
        uri_id = pubkey.data_b64
        uri_s = pubkey.data_b64_s
        fnfn = commie.save_uri_as_qrcode(uri_id=uri_id,name=name)
        
        # await logfunc(f'Here. I have cut for you a private and public asymmetric key pair, using the iron-clad Elliptic curve algorithm:',comrad_name='Keymaker')

        await logfunc(f'The first is your "public key", which you can share with anyone. With it, someone can write you an encrypted message.',comrad_name='Keymaker')
        
        

        # delete qr!
        os.remove(fnfn)

        # await logfunc(f'(1) {pubkey} -- and -- (2) {privkey}',clear=True,pause=True,comrad_name='Keymaker')

        # await logfunc(f'(1) You may store your public key both on your device hardware, as well as share it with anyone you wish: {pubkey.data_b64_s}') #\n\nIt will also be stored as a QR code on your device:\n{qr_str}',pause=True,clear=True)
        


        commie._keychain['pubkey']=pubkey
        commie._keychain['privkey']=privkey
        
        from comrad.utils import dict_format
        self.log('My keychain now looks like:' + dict_format(commie.keychain()))
        # return




        ### PRIVATE KEY
        
       

        # ### PUBLIC KEY
        await logfunc('You can now register your username and public key with Comrad @Operator on the remote server.',pause=False,clear=False)

        await logfunc('Connecting you to the @Operator...',comrad_name='Telephone')

        ## CALL OP WITH PUBKEY
        # self.app.open_dialog('Calling @Operator...')
        logger.info('got here!')
        resp_msg_d = await self.app.ring_ring(
            {
                'name':name, 
                'pubkey': pubkey.data,
            },
            route='register_new_user',
            commie=commie
        )
        
        # self.app.close_dialog()
        
        
        # print()
        await logfunc(resp_msg_d.get('status'),comrad_name='Operator',pause=True)

        if not resp_msg_d.get('success'):
            self.app.comrad=None
            self.app.is_logged_in=False
            self.app.username=''
            
            await logfunc('''That's too bad. Cancelling registration for now.''',pause=True,clear=True)
            
            # self.app.change_screen('feed')
            self.app.change_screen('login')
            return

        # we're good on public key front
        commie.name=resp_msg_d.get('name')
        pubkey_b = resp_msg_d.get('pubkey')
        assert pubkey_b == pubkey.data
        uri_id = pubkey.data_b64
        sec_login = resp_msg_d.get('secret_login')
        _fnfn=commie.save_uri_as_qrcode(uri_id)
        commie.crypt_keys.set(name, pubkey_b, prefix='/pubkey/')
        commie.crypt_keys.set(uri_id, name, prefix='/name/')
        commie.crypt_keys.set(uri_id,sec_login,prefix='/secret_login/')
        


        await logfunc('Great. Comrad @Operator now has your name and public key on file (and nothing else!).',pause=True,clear=True)

        await logfunc(f'You can share it by pasting it to someone in a secure message:\n{uri_s}',comrad_name='Keymaker')
        
        await logfunc(f'You can also share it IRL, phone to phone, as a QR code. It is saved to {fnfn} and looks like this.',img_src=fnfn,comrad_name='Keymaker')





        ## PRIVATE KEY

        await logfunc(f"Your PRIVATE encryption key, on the other hand, will be stored only on your device hardware. Do not share it with anyone or across any network whatsoever.")
        await logfunc(f"In fact this private encryption is so sensitive we'll encrypt it before storing it on your device.",pause=True,use_prefix=False)
        
        passphrase = await self.app.get_input('Please enter a memorable password.',get_pass=True)
        if not passphrase or not str(passphrase).strip():
            return {'success':False, 'status':'No password entered'}

        passhash = hasher(str(passphrase).strip())
        privkey_decr = ComradSymmetricKeyWithPassphrase(passhash=passhash)
        print()
        
        await logfunc(f'''We immediately run whatever you typed through a 1-way hashing algorithm (SHA-256), scrambling it into (redacted):\n{make_key_discreet_str(passhash)}''',pause=True,clear=False)

        privkey_encr = privkey_decr.encrypt(privkey.data)
        privkey_encr_obj = ComradEncryptedAsymmetricPrivateKey(privkey_encr)
        commie._keychain['privkey_encr']=privkey_encr_obj
        self.log('My keychain now looks like v2:',dict_format(commie.keychain()))

       
        await logfunc(f'With this scrambled password we can encrypt your super-sensitive private key to (redacted):\n{privkey_encr_obj.discreet}',pause=True,clear=False)

        # store privkey pieces
        commie.crypt_keys.set(uri_id, privkey_encr_obj.data, prefix='/privkey_encr/')
        # just to show we used a passphrase -->
        commie.crypt_keys.set(uri_id, ComradSymmetricKeyWithPassphrase.__name__, prefix='/privkey_decr/')


        # save qr too:
        # await logfunc(f'Saving public key, encrypted private key, and login secret to hardware-only database. Also saving public key as QR code to: {_fnfn}.',pause=True,clear=False,use_prefix=False)

        # done!
        await logfunc(f'Congratulations. Welcome, Comrad @{commie.name}.',pause=True,clear=True)
        
        # remove all dialogs!!!!!!!!
        # last minute: get posts
        if 'res_posts' in resp_msg_d and resp_msg_d['res_posts'].get('success'):
            id2post=resp_msg_d.get('res_posts').get('posts',{})
            if id2post:
                commie.log('found starter posts:',list(id2post.keys()))
            commie.save_posts(id2post)
            resp_msg_d['status']+=f'  You\'ve got {len(id2post)} new posts and 0 new messages.'
        


        # await logfunc('Returning...')

        from comrad.app.screens.map import MapWidget
        if self.app.map:
            self.app.map.dismiss()
            self.app.map=None
        self.app.change_screen('feed')
        
        return resp_msg_d

    

















class TextfieldLabel(ThemableBehavior, Label):
    font_style = OptionProperty("Body1", options=theme_font_styles)
    # <kivymd.uix.textfield.MDTextField object>
    field = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = sp(self.theme_cls.font_styles[self.font_style][1])
