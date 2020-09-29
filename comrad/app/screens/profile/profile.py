import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from comrad import *

from screens.base import BaseScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.chip import MDChip
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton,MDRectangleFlatIconButton,MDIconButton
from kivymd.uix.label import MDLabel, MDIcon
from kivy.uix.image import AsyncImage, Image
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
import io,asyncio
from kivy.uix.carousel import Carousel
from screens.feed.feed import PostCard
from kivy.clock import Clock
from functools import partial
from copy import copy,deepcopy
from kivy.animation import Animation
from main import MyLabel,COLOR_ICON
from misc import *



class ProfileAvatar(Image):
    def on_touch_down(self, touch):
        if self.screen.carousel.index and self.collide_point(*touch.pos) and self.screen.carousel.slides:
            start = self.screen.carousel.slides[0]
            start.opacity=0
            self.screen.carousel.index=0
            anim = Animation(opacity=1, duration=0.1)
            anim.start(start)
            # start = self.screen.carousel.slides[0]
            # log('????',start)
            # self.screen.carousel.load_slide(start)
            # self.screen.carousel.load_next()

class LayoutAvatar(MDBoxLayout): pass

class AuthorInfoLayout(MDBoxLayout): pass

class LayoutCover(MDBoxLayout): 
    source=StringProperty()
    pass

class CoverImage(Image): pass



def binarize_image(image, threshold=200):
    """Binarize an image."""
    image = image.convert('L')  # convert image to monochrome
    import numpy
    image = numpy.array(image)
    image = binarize_array(image, threshold)
    imsave(target_path, image)
    return image

def binarize_array(numpy_array, threshold=200):
    """Binarize a numpy array."""
    import numpy
    for i in range(len(numpy_array)):
        for j in range(len(numpy_array[0])):
            if numpy_array[i][j] > threshold:
                numpy_array[i][j] = 255
            else:
                numpy_array[i][j] = 0
    return numpy_array




def crop_square(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def circularize_img(img_fn, width, im=None, do_crop=True,bw=False,resize=True,circularize=True):
    from PIL import Image, ImageOps, ImageDraw
    from kivy.app import App
    import numpy as np
    log=App.get_running_app().log

    #if not im: 
    im = Image.open(img_fn)
    log('??',im)
    
    

    # get center
    if do_crop: im = crop_square(im, width, width)
    if resize: im = im.resize((width,width))

    if bw:
        thresh = 175
        fn = lambda x : 255 if x > thresh else 0
        im = im.convert('L').point(fn, mode='1').convert('RGB')
        orig_color = (255,255,255)
        replacement_color = COLOR_ICON #(255,0,0)
        # img = im.convert('RGB')
        data = np.array(im)
        data[(data == orig_color).all(axis = -1)] = replacement_color
        im = Image.fromarray(data, mode='RGB').convert('RGBA')
    
    if circularize_img:
        bigsize = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        im.putalpha(mask)


    # give back bytes
    

    log('!!',im)

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

class ProfilePageLayout(MDBoxLayout): pass
class FollowerLayout(MDBoxLayout): pass

class AuthorName(MyLabel): pass
class AuthorUsername(MyLabel): pass
class AuthorDesc(MyLabel): pass
class AuthorPronouns(MyChip): pass
class AuthorPlace(MyChip): pass
class AuthorWebsite(MyChip): pass
class AuthorFollowers(MyChip): pass
class AuthorFollowing(MyChip): pass



def update_screen_on_carousel_move(self,dt,width=75):
    
    # screen.author_name.text=str(screen.carousel.index)
    # avatar_layout = copy(screen.avatar_layout)
    # avatar_layout.width=dp(100)
    # avatar_layout.height=dp(100)
    
    if self.carousel.index:
        if not hasattr(self,'avatar_layout_small'):
            self.avatar_img.seek(0)
            img,byte,avatar,avatar_layout = self.make_profile_img(width,do_crop=False,bw=True,circularize=False)
            avatar.screen = self
            avatar_layout.pos_hint = {'right':0.995, 'top':0.995}
            avatar_layout.opacity=0
            # avatar_layout.animate()
            self.add_widget(avatar_layout)
            self.avatar_layout_small=avatar_layout
            self.avatar_layout_small_visible=False
            
        if not self.avatar_layout_small_visible:
            self.avatar_layout_small_visible=True 
            anim = Animation(opacity=1, duration=0.25)
            anim.start(self.avatar_layout_small)

    else:
        if hasattr(self,'avatar_layout_small'):
            if self.avatar_layout_small_visible:
                self.avatar_layout_small_visible=False
                anim = Animation(opacity=0, duration=0.25)
                anim.start(self.avatar_layout_small)
            
            # self.remove_widget(self.avatar_layout_small)
            # del self.avatar_layout_small

    # avatar_layout = self.avatar_layout
    # self.remove_widget(avatar_layout)
    # self.add_widget(avatar_layout)



from screens.base import ProtectedScreen
class ProfileScreen(ProtectedScreen): 
    username = None
    clock_scheduled=None

   
    def make_profile_img(self,width,do_crop=True,circ_img=None,bw=False,circularize=True):
        img_src = os.path.join(PATH_GUI_ASSETS, 'avatars', f'{self.app.username}.png')
        if not os.path.exists(img_src): 
            img_src=PATH_DEFAULT_AVATAR
        
        circ_img = circularize_img(img_src,width,do_crop=do_crop,bw=bw,circularize=circularize)
        avatar_layout = LayoutAvatar()
        byte=io.BytesIO(circ_img.read())


        img = CoreImage(byte,ext='png')
        avatar = ProfileAvatar()
        avatar.texture = img.texture
        avatar_layout.height=dp(width)
        avatar_layout.width=dp(width)
        avatar_layout.add_widget(avatar)
        return (circ_img,byte,avatar,avatar_layout) 

    def on_pre_enter(self, width=300):
        if not super().on_pre_enter(): return

        if not self.clock_scheduled:
            Clock.schedule_interval(partial(update_screen_on_carousel_move, self), 0.1)
            self.clock_scheduled=True


        # clear
        if hasattr(self,'carousel'):
            for post in self.posts:
                self.carousel.remove_widget(post)
            self.remove_widget(self.carousel)
            del self.carousel
            self.posts=[]
            
    
        self.carousel = Carousel()
        self.carousel.direction='right'
        self.carousel.loop=True
        self.posts=[]
            
        # get circular image
        self.avatar_img, self.avatar_img_bytes, self.avatar, self.avatar_layout = \
            self.make_profile_img(width)
        self.avatar.screen = self

        ## author info
        self.author_info_layout = AuthorInfoLayout()
        #self.app.name_irl = 'Marx Zuckerberg'
        self.app.name_irl = 'Comrad @'+self.app.username
        
        if hasattr(self.app,'name_irl'):
            self.author_name_irl = AuthorName(text=self.app.name_irl)
            self.author_name_irl.font_name = 'assets/font.otf'
            self.author_name_irl.font_size = '28sp'
            self.author_info_layout.add_widget(self.author_name_irl)
        
        self.author_name = AuthorUsername(text='@'+self.app.username)
        self.author_name.font_name = 'assets/font.otf'
        self.author_name.font_size = '20sp'
        # self.author_info_layout.add_widget(self.author_name)


        ## AUTHOR DESCRIPTION
        self.author_desc = AuthorDesc(text='... etc ...')
        self.author_desc.font_name='assets/font.otf'
        self.author_desc.font_size='18sp'
        # self.author_desc.halign='left'

        ## Pronouns
        self.author_pronouns = AuthorPronouns(label='he/him',icon='gender-transgender')

        ## AUTHOR PLACE
        self.author_place = AuthorPlace(label='Earth',icon='map-marker-outline')

        ## Website
        self.author_website = AuthorWebsite(label='website.org', icon='link-variant')


        ## Followers
        self.follower_layout = FollowerLayout()
        # self.author_followers = AuthorFollowers(label='13 followers',icon='account-arrow-left')
        self.author_following = AuthorFollowing(label='13 comrads',icon='account-multiple')


        ## add to layout
        self.author_info_layout.add_widget(self.author_desc)
        self.author_info_layout.add_widget(self.author_pronouns)
        self.author_info_layout.add_widget(self.author_place)
        # self.author_info_layout.add_widget(self.author_website)
               
        self.follower_layout.add_widget(self.author_following)
        # self.follower_layout.add_widget(self.author_followers) 
        self.author_info_layout.add_widget(self.follower_layout)

        # class AuthorPlace(MDLabel): pass
        # class AuthorWebsite(MDLabel): pass
        # class AuthorFollowers(MDLabel): pass
        # class AuthorFollowing(MDLabel): pass

        
        
        
        ## add root widgets
        self.page_layout = ProfilePageLayout()
        self.page_layout.add_widget(self.avatar_layout)
        self.page_layout.add_widget(self.author_info_layout)
        
        self.add_widget(self.carousel)
        self.carousel.add_widget(self.page_layout)

        ## add posts
        asyncio.create_task(self.add_author_posts())

    async def add_author_posts(self):
        # add posts
        lim=25
        posts=await self.app.get_my_posts()
        self.log('POSTS!?',posts)
        # stop
        for i,post in enumerate(posts):
            if i>lim: break
            
            post_obj = PostCard(post)
            self.log(post)
            self.posts.append(post_obj)
            self.carousel.add_widget(post_obj)

    # def on_touch_move(self, ent):
    #     if self.carousel.index:
    #         self.author_name.text='moved!'
    #     else:
    #         self.author_name.text=self.username