from kivymd.uix.label import MDLabel
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard, MDSeparator
from kivy.uix.scrollview import ScrollView
from screens.base import ProtectedScreen
from kivy.properties import ListProperty
from main import log
import os
from kivy.app import App
    

### POST CODE
class PostTitle(MDLabel): pass
class PostGridLayout(GridLayout): pass
class PostImage(AsyncImage): pass

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
class PostAuthorAvatar(AsyncImage): pass

class PostLayout(MDBoxLayout): pass

class PostScrollView(ScrollView): pass

class PostCard(MDCard):
    def __init__(self, author = None, title = None, img_src = None, content = None):
        super().__init__()
        self.author = author
        self.title = title
        self.img_src = img_src if img_src else ''
        self.cache_img_src = os.path.join('cache','img',img_src) if img_src else ''
        self.img_loaded = os.path.exists(self.cache_img_src)
        self.content = content
        self.bind(minimum_height=self.setter('height'))

        # pieces
        author_section_layout = PostAuthorLayout()
        author_label = PostAuthorLabel(text=self.author)
        author_label.font_size = '28dp'
        author_avatar = PostAuthorAvatar(source='avatar.jpg') #self.img_src)
        author_section_layout.add_widget(author_avatar)
        author_section_layout.add_widget(author_label)
        # author_section_layout.add_widget(author_avatar)
        # self.add_widget(author_section_layout)

        if self.cache_img_src:
            image_layout = PostImageLayout()
            self.image = image = PostImage(source=self.cache_img_src)
            image.height = '300dp'
            image_layout.add_widget(image)
            image_layout.height='300dp'
            # log(image.image_ratio)

        content = PostContent(text=self.content)
        
        # post_layout = PostGridLayout()
        #content = PostContent()

        # add to screen
        # self.add_widget(title)
        # post_layout.add_widget(author_section_layout)
        # post_layout.add_widget(image_layout)
        # post_layout.add_widget(content)

        
        scroller = PostScrollView()
        self.add_widget(author_section_layout)
        # self.add_widget(MDLabel(text='hello'))
        log('img_src ' + str(bool(self.img_src)))
        if self.img_src: self.add_widget(image_layout)

        def estimate_height(minlen=100,maxlen=500):
            num_chars = len(self.content)
            # num_lines = num_chars
            height = num_chars*1.1
            if height>maxlen: height=maxlen
            if height<minlen: height=minlen
            return height

        scroller.size = ('300dp','%sdp' % estimate_height())
        

        # scroller.bind(size=('300dp',scroller.setter('height'))
        scroller.add_widget(content)
        self.add_widget(scroller)
        # self.add_widget(post_layout)

    @property
    def app(self):
        return App.get_running_app()

    def load_image(self):
        if not self.img_src: return
        if self.img_loaded: return
        
        # otherwise load image...
        self.app.get_image(self.img_src)
        log('done getting image!')
        self.image.reload()
        self.img_loaded=True

#####


class FeedScreen(ProtectedScreen):
    posts = ListProperty()

    def on_pre_enter(self):
        # log('ids:' +str(self.ids.post_carousel.ids))
        for post in self.posts:
            log('post: '+str(post))
            self.ids.post_carousel.remove_widget(post)
        
        i=0
        lim=25
        for i,post in enumerate(reversed(self.app.get_posts())):
            log('third?')
            #if ln.startswith('@') or ln.startswith('RT '): continue
            #i+=1
            if i>lim: break
            
            #post = Post(title=f'Marx Zuckerberg', content=ln.strip())
            post_obj = PostCard(
                author='Marx Zuckerberg',
                title='',
                img_src=post.get('img_src',''),
                content=post.get('content',''))
            log(post)
            self.posts.append(post_obj)
            self.ids.post_carousel.add_widget(post_obj)

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

    