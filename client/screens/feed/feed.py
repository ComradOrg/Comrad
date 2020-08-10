from kivymd.uix.label import MDLabel
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from screens.base import ProtectedScreen


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

class PostAuthorLabel(MDLabel): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.bind(texture_size=self.setter('size'))
        self.font_name='assets/overpass-mono-regular.otf'
    pass
class PostAuthorAvatar(AsyncImage): pass

class PostCard(MDCard):
    def __init__(self, author = None, title = None, img_src = None, content = None):
        super().__init__()
        self.author = author
        self.title = title
        self.img_src = img_src
        self.content = content
        self.bind(minimum_height=self.setter('height'))

        # pieces
        author_section_layout = PostAuthorLayout()
        author_label = PostAuthorLabel(text=self.author)
        author_label.font_size = '28dp'
        author_avatar = PostAuthorAvatar(source=self.img_src)
        author_section_layout.add_widget(author_avatar)
        author_section_layout.add_widget(author_label)
        # author_section_layout.add_widget(author_avatar)
        self.add_widget(author_section_layout)

        
        title = PostTitle(text=self.title)
        # image = PostImage(source=self.img_src)
        content = PostContent(text=self.content)
        
        #content = PostContent()

        # add to screen
        self.add_widget(title)
        # self.add_widget(image)
        self.add_widget(content)
        #self.add_widget(layout)

#####


class FeedScreen(ProtectedScreen):
    def on_enter(self):
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
