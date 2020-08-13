from screens.base import BaseScreen
from main import log
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivy.uix.image import AsyncImage, Image
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
import io

img_src = 'assets/avatar.jpg' #cache/img/1e6/587e880344d1e88cec8fda65b1148.jpeg'
# img_src = '/home/ryan/Pictures/Harrier.jpeg'
cover_img_src='assets/cover.jpg' #cache/img/60d/9de00e52e4758ade5969c50dc053f.jpg'

class ProfileAvatar(Image): pass

class LayoutAvatar(MDBoxLayout): pass

class LayoutCover(MDBoxLayout): 
    source=StringProperty()
    pass

class CoverImage(Image): pass

def crop_square(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def circularize_img(img_fn, width):
    from PIL import Image, ImageOps, ImageDraw
    

    im = Image.open(img_fn)

    # get center
    im = crop_square(im, width, width)
    im = im.resize((width,width))
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)

    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
    imgByteArr = io.BytesIO()
    output.save(imgByteArr, format='PNG')
    # imgByteArr = imgByteArr.getvalue()
    imgByteArr.seek(0)
    return imgByteArr
    # output.putalpha(mask)
    # output.save('output.png')

    # background = Image.open('back.jpg')
    # background.paste(im, (150, 10), im)
    # background.save('overlap.png')
    # return output



class ProfileScreen(BaseScreen): 
    #def on_pre_enter(self):
    #    global app
    #    if app.is_logged_in():
    #        app.root.change_screen('feed')
    def on_pre_enter(self, do_cover_img=False, width=200):
        # get circular image
        circ_img = circularize_img(img_src,200)
        self.avatar_layout = LayoutAvatar()
        img = CoreImage(io.BytesIO(circ_img.read()),ext='png')
        self.avatar = ProfileAvatar()
        self.avatar.texture = img.texture
        self.avatar_layout.height=dp(width)
        self.avatar_layout.width=dp(width)
        self.avatar_layout.add_widget(self.avatar) 

        if do_cover_img:
            self.cover_image = CoverImage(source=cover_img_src)
            self.cover_layout = LayoutCover(source=cover_img_src)
            # max width
            coverwidth = dp(Window.size[0])
            coverheight = dp(Window.size[0] / self.cover_image.image_ratio)
            # self.cover_layout.size=(coverwidth,coverheight)
            self.cover_image.width=dp(coverwidth)
            self.cover_image.height=dp(coverheight)
            self.cover_layout.width = dp(coverwidth)
            self.cover_layout.height = dp(coverheight)
            self.cover_layout.add_widget(self.cover_image)
            self.add_widget(self.cover_layout)
            self.avatar_layout.pos_hint = {'center_x':0.2,'center_y':0.8}

        self.add_widget(self.avatar_layout)


    