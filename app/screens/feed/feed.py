from kivymd.uix.label import MDLabel
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage, Image
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard, MDSeparator
from kivy.uix.scrollview import ScrollView
from screens.base import ProtectedScreen,BaseScreen
from kivy.properties import ListProperty
import os,time
from datetime import datetime
from kivy.app import App
from threading import Thread
import asyncio



### POST CODE
class PostTitle(MDLabel): pass
class PostGridLayout(GridLayout): pass
class PostImage(AsyncImage): pass
# class PostImage(CoreImage)
class PostImageBytes(Image): pass

class PostContent(MDLabel): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.bind(texture_size=self.setter('size'))
        self.font_name='assets/overpass-mono-regular.otf'
    #pass

class PostAuthorLayout(MDBoxLayout): pass

class PostImageLayout(MDBoxLayout): pass


class PostAuthorLabel(MDLabel): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.bind(texture_size=self.setter('size'))
        self.font_name='assets/overpass-mono-regular.otf'
    pass

class PostTimestampLabel(MDLabel): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.bind(texture_size=self.setter('size'))
        self.font_name='assets/overpass-mono-regular.otf'

class PostAuthorAvatar(AsyncImage): pass

class PostLayout(MDBoxLayout): pass

class PostScrollView(ScrollView): pass

class PostCard(MDCard):
    @property
    def app(self): return App.get_running_app()
    def log(self,*x): self.app.log(*x)

    def __init__(self, data):
        super().__init__()
        # self.log('PostCard() got data: '+str(data))
        self.author = data.get('author','[Anonymous]')
        self.img_id = data.get('file_id','')
        self.img_ext = data.get('file_ext','')
        self.img_src=self.img_id[:3]+'/'+self.img_id[3:]+'.'+self.img_ext if self.img_id else ''
        self.cache_img_src = os.path.join('cache',self.img_src) if self.img_src else ''
        self.img_loaded = os.path.exists(self.cache_img_src)
        self.content = data.get('content','')
        self.timestamp = data.get('timestamp',None)
        self.bind(minimum_height=self.setter('height'))

        # self.log('PostCard.img_id =',self.img_id)
        # self.log('PostCard.img_ext =',self.img_ext)
        # self.log('PostCard.img_src =',self.img_src)
        # self.log('PostCard.cache_img_src =',self.cache_img_src)

        # pieces
        self.author_section_layout = author_section_layout = PostAuthorLayout()
        self.author_label = author_label = PostAuthorLabel(text='@'+self.author)
        self.author_label.font_size = '18sp'
        self.author_avatar = author_avatar = PostAuthorAvatar(source='assets/avatar.jpg') #self.img_src)
        self.author_section_layout.add_widget(author_avatar)
        self.author_section_layout.add_widget(author_label)

        # timestamp
        timestr=''
        #log(self.timestamp)
        if self.timestamp:
            dt_object = datetime.fromtimestamp(self.timestamp)
            timestr = dt_object.strftime("%-d %b %Y %H:%M") 
        #log('timestr: '+timestr)
        author_section_layout.add_widget(PostTimestampLabel(text=timestr))
        # author_section_layout.add_widget(author_avatar)
        # self.add_widget(author_section_layout)

        if self.cache_img_src:
            image_layout = PostImageLayout()
            self.image = image = PostImage(source=self.cache_img_src)
            image.height = '300sp'
            image_layout.add_widget(image)
            image_layout.height='300sp'
            # self.log(image.image_ratio)

        self.post_content = PostContent(text=self.content)
        
        # post_layout = PostGridLayout()
        #content = PostContent()

        # add to screen
        # self.add_widget(title)
        # post_layout.add_widget(author_section_layout)
        # post_layout.add_widget(image_layout)
        # post_layout.add_widget(content)

        
        self.scroller = scroller = PostScrollView()
        self.add_widget(author_section_layout)
        # self.add_widget(MDLabel(text='hello'))
        #log('img_src ' + str(bool(self.img_src)))
        if self.img_src: self.add_widget(image_layout)

        def estimate_height(minlen=100,maxlen=500):
            num_chars = len(self.content)
            # num_lines = num_chars
            height = num_chars*1.1
            if height>maxlen: height=maxlen
            if height<minlen: height=minlen
            return height

        scroller.size = ('300sp','%ssp' % estimate_height())
        

        # scroller.bind(size=('300sp',scroller.setter('height'))
        scroller.add_widget(self.post_content)
        self.add_widget(scroller)
        # self.add_widget(post_layout)

        # self.log('?????',self.cache_img_src, os.path.exists(self.cache_img_src), os.stat(self.cache_img_src).st_size)
        if self.cache_img_src and (not os.path.exists(self.cache_img_src) or not os.stat(self.cache_img_src).st_size):
            async def do_download_later():
                self.log('downloading...')
                await self.app.download(self.img_id, self.cache_img_src)
                self.image.reload()
                return True

            #self.open_dialog('posting')
            #Thread(target=do_download).start()
            asyncio.create_task(do_download_later())


    @property
    def app(self):
        return App.get_running_app()

    def load_image(self):
        if not self.img_src: return
        if self.img_loaded: return
        
        # otherwise load image...
        self.app.get_image(self.img_src)
        self.log('done getting image!')
        self.image.reload()
        self.img_loaded=True

#####


class FeedScreen(BaseScreen):
    posts = ListProperty()

    def on_pre_enter(self):
        super().on_pre_enter()
        
        async def go():
            # self.log('ids:' +str(self.ids.post_carousel.ids))
            for post in self.posts:
                self.ids.post_carousel.remove_widget(post)
            
            i=0
            lim=25
            posts=await self.app.get_posts()
            for i,post in enumerate(reversed(posts)):
                #if ln.startswith('@') or ln.startswith('RT '): continue
                #i+=1
                if i>lim: break
                
                #post = Post(title=f'Marx Zuckerberg', content=ln.strip())
                self.log('???')
                post_obj = PostCard(post)
                self.posts.append(post_obj)
                self.ids.post_carousel.add_widget(post_obj)
        asyncio.create_task(go())

    def on_pre_enter_test(self):
        i=0
        lim=5
        with open('tweets.txt') as f:
            for ln in f:
                if ln.startswith('@') or ln.startswith('RT '): continue
                i+=1
                if i>lim: break
                
                #post = Post(title=f'Marx Zuckerberg', content=ln.strip())
                post = PostCard(
                    author='Marx Zuckerberg',
                    title='',
                    img_src='avatar.jpg',
                    content=ln.strip())
                print(post)
                self.ids.post_carousel.add_widget(post)

    