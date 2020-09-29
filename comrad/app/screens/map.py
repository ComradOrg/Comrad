import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..','..')))
from comrad.app.screens.dialog import MDDialog2
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
print('\n'.join(sys.path))
from comrad.constants import *
# from comrad.app.main import rgb
import io
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image,AsyncImage
from kivy.core.window import Window
from kivy.app import App
import logging
logger=logging.getLogger(__name__)

def rgb(r,g,b,a=1):
    return (r/255,g/255,b/255,a)

class MapImage(AsyncImage):
    pass


class MapWidget(MDDialog2):
    @property
    def projection(self):
        # return ccrs.PlateCarree()
        return ccrs.EckertI()
    
    @property
    def figsize(self):
        # fig = plt.figure()
        # dpi=fig.dpi // 2
        dpi=40
        width,height=Window.size
        return (width//dpi, height//dpi)
        # bbox = fig.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        # width, height = bbox.width*fig.dpi, bbox.height*fig.dpi
        # return (width,height)

    @property
    def color_land(self): return rgb(*darksienna3,a=0) #darksienna3)
    @property
    def color_water(self): return rgb(*russiangreen)
    @property
    def color_label(self): return rgb(*COLOR_ICON)
    @property
    def color_marker(self): return rgb(*COLOR_ICON)
    @property
    def color_line(self): return rgb(*COLOR_ICON)

    def __init__(self):
        self.last_lat = None
        self.last_long = None
        self.points = []
        self.opened=False
        self.label=None
        self.intro_label=None

        # self.fig = fig = plt.figure(figsize=(20,10))
        plt.rcParams["figure.figsize"] = self.figsize
        self.ax = ax = plt.axes(
            projection=self.projection,
        )
        # ax.set_extent([-170, 165, -55, 75])
        
        # ax.background_patch.set_facecolor(rgb(*COLOR_CARD)[:3])
        # ax.outline_patch.set_facecolor(rgb(*COLOR_CARD)[:3])
        # self.ax.stock_img()
        # self.ax.coastlines(color=rgb(*COLOR_CARD))
        ax.add_feature(cartopy.feature.OCEAN, zorder=0, color=self.color_water,edgecolor=self.color_water)
        ax.add_feature(cartopy.feature.LAND, zorder=0, color=self.color_land, edgecolor=self.color_land)
        ax.outline_patch.set_visible(False)
        ax.background_patch.set_visible(False)
        # ax.set_global()
        # ax.gridlines()


        self.layout=MDBoxLayout()
        self.layout.orientation='vertical'
        self.layout.cols=1
        self.layout.size_hint=(None,None)
        self.layout.size=(Window.size[0],Window.size[1]) # ('666sp','666sp')
        self.layout.md_bg_color=rgb(*eerieblack) #rgb(*COLOR_BG,a=1)
        # self.layout.adaptive_height=True
        # self.layout.height=self.layout.minimum_height
        self.layout.spacing='0sp'
        self.layout.padding='0sp'
        self.img=None
        self.label_layout=MDGridLayout()
        self.label_layout.orientation='vertical'
        self.label_layout.cols=1
        self.label_layout.row_default_height='25sp'
        self.label_layout.row_force_default='25sp'
        self.label_layout.rows=10
        self.label_layout.pos_hint={'y':0}
        self.label_layout.size_hint=(None,None)
        self.label_layout.width=Window.size[0]
        self.label_layout.height='300sp'
        # self.label_layout.size=(Window.size[0],'400sp')
        # self.label_layout.size=Window.size # ('666sp','666sp')
        # self.layout.add_widget(self.label_layout)

        # do dialog's intro
        super().__init__(
            type='custom',
            text='',
            content_cls=self.layout,
            buttons=[
                MDFlatButton(
                    text="disconnect",
                    text_color=rgb(*COLOR_TEXT),
                    md_bg_color = rgb(*eerieblack), #(0,0,0,1),
                    theme_text_color='Custom',
                    on_release=self.dismiss,
                    font_name=FONT_PATH
                )
            ],
            color_bg = rgb(*eerieblack), #(0,0,0,1),
            overlay_color=(0,0,0,0),
            background_color=(0,0,0,0)
        )
        self.ids.text.text_color=rgb(*COLOR_TEXT)
        self.ids.text.font_name=FONT_PATH
        self.size=Window.size #('666sp','666sp')
        # self.
        # self.adaptive_height=True

    def draw(self):
        from matplotlib import transforms
        from PIL import Image as pImage
        from PIL import ImageOps
        tr = transforms.Affine2D().rotate_deg(90)


        # buf = io.BytesIO()
        # plt.ion()
        from comrad.constants import PATH_MAPS
        odir=PATH_MAPS
        if not os.path.exists(odir): os.makedirs(odir)
        ofn=os.path.join(odir,f't_{len(self.points)}.png')
        # plt.gca().invert_yaxis()
        plt.savefig(ofn, format='png',transparent=True,pad_inches=0.1,bbox_inches = 'tight')

        # flip?
        # im = pImage.open(ofn)
        # im = im.rotate(90)
        # im.save(ofn)

        if not self.img:
            self.img= AsyncImage(source=ofn)
            self.img.background_color=(0,0,0,0)
            self.img.overlay_color=(0,0,0,0)
            # self.img.texture.flip_horizontal()
            self.img.pos_hint={'center_x':0.48,'center_y':0.5}
            # self.img.size=Window.size
            # self.img.texture = img
            self.img.add_widget(self.label_layout,1)
            self.layout.add_widget(self.img,1)
            
        else:
            self.img.source=ofn
        # self.img.size_hint=(1,1)
        # self.img.width=Window.size[0]
        # self.img.allow_stretch=True

    def makelabel(self,txt):
        label=MDLabel(text=txt)
        label.color=self.color_label #rgb(*color) #self.color_label
        label.font_name=FONT_PATH
        label.font_size='20sp'
        # label.size_hint=(1,1)
        label.width=Window.size[0]
        label.height='25sp'
        label.valign='top'
        return label

    def add_point(self,lat,long,desc):
        logger.info(f'adding point? {desc} {lat}, {long}')
        # plt.text(
        #     long+3,
        #     lat-12,
        #     desc,
        #     horizontalalignment='left',
        #     transform=self.projection
        # )
        import random
        from comrad.constants import ALL_COLORS
        color = random.choice(ALL_COLORS)
        self.points+=[(lat,long,desc)]
        
        # point
        plt.plot(
            long,
            lat,
            '+',
            markersize=25,
            linewidth=10,
            color=self.color_marker,#rgb(*color),
            transform=ccrs.Geodetic(),
        )

        # line
        if self.last_lat and self.last_long:
            self.ax.lines = []
            plt.plot(
                [self.last_long, long],
                [self.last_lat, lat],
                color=self.color_line,#rgb(*color), #self.color_line,
                linewidth=4, marker='',
                transform=ccrs.Geodetic(),
            )

        
        desc = '\n'.join('--> '+desc for lat,long,desc in self.points[-1:])
        #if self.label:
        #    self.img.remove_widget(self.label)

        self.label=label=self.makelabel(desc)
        # label.height='400sp'
        # label.pos_hint = {'center_y':0.1+(0.1 * len(self.points))}
        # label.pos = (0.5,0)
        self.label_layout.add_widget(label)

        
        
        self.last_lat,self.last_long = lat,long
        self.ax.set_global()


    # wait and show
    def open(self,maxwait=666,pulse=0.1):
        self.draw()
        if not self.intro_label:
            self.intro_label = self.makelabel('Routing you through the global maze of Tor ...')
            self.label_layout.add_widget(self.intro_label)
        super().open()
        self.opened=True
        # await asyncio.sleep(pulse)
        # waited=0
        # while not self.ok_to_continue:
        #     await asyncio.sleep(pulse)
        #     waited+=pulse
        #     if waited>maxwait: break
        #     # logger.info(f'waiting for {waited} seconds... {self.ok_to_continue} {self.response}')
        # return self.response

    def dismiss(self):
        super().dismiss()
        self.intro_label=None
        if hasattr(self.layout,'img'):
            self.layout.remove_widget(self.img)
        if self.layout:
            self.remove_widget(self.layout)

default_places = {
    'Cambridge':(52.205338,0.121817),
    'Sydney':(-33.868820,151.209290),
    'New York':(40.712776,-74.005974),
    'Hong Kong':(22.278300,114.174700),
    'Cape Town':(-33.9249, 18.4241),
    'San Francisco':(37.774929,-122.419418),
    'Honolulu':(21.306944,-157.858337),
    'Tokyo':(35.689487,139.691711),
    'Ushuaia':(-54.801910,-68.302948),
    'Reykjavik':(64.126518,-21.817438)

}


def test_map():
    map = MapWidget()
    plt.show()


if __name__=='__main__':

    test_map()