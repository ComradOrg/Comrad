# Code from 
# https://github.com/snorfalorpagus/ascii-world-map
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))

import json
from functools import partial
from shutil import get_terminal_size
from shapely.geometry import shape, Point
from shapely import ops
import pyproj,math,os
import rtree
import curses,random,time
from comrad.utils import Logger
import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings(action='ignore')

PLACE_MARKER='@'
BASEMAP_MARKER='_'
PATH_MARKER='+'

# # read the data into a list of shapely geometries
# with open(os.path.join(os.path.dirname(__file__),"data/world-countries2.json")) as f:
#     data = json.load(f)


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


# print_map(['Brazil','Netherlands','Thailand'])
# print_map_simple(places)

class Map(Logger):

    def __init__(self,stdscr):
        self.stdscr=stdscr
        self.base_df=None
        self.last_coords=None
        self.stdscr.clear()

    @property
    def width(self):
        return get_terminal_size().columns - 1
        # from comrad.constants import CLI_WIDTH
        # return CLI_WIDTH

    @property
    def height(self):
        return get_terminal_size().lines - 1
        # from comrad.constants import CLI_HEIGHT
        # return CLI_HEIGHT

    def precompute_basemap(self,countries=[]):
        data_fn=os.path.join(
            os.path.dirname(__file__),
            "data/world-countries.json"
        )
        with open(data_fn) as f:
            data = json.load(f)

        geoms = [
            shape(feature["geometry"])
            for feature in data["features"]
        ]
        
        # transform the geometries into web mercator
        wgs84 = pyproj.Proj(init="EPSG:4326")
        webmerc = pyproj.Proj(proj="webmerc")
        t = partial(pyproj.transform, wgs84, webmerc)
        geoms = [ops.transform(t, geom) for geom in geoms]

        # create a spatial index of the geometries
        def gen(geoms):
            for n, geom in enumerate(geoms):
                yield n, geom.bounds, geom
        index = rtree.index.Index(gen(geoms))

        # get the window size
        columns = self.width
        lines = self.height  # allow for prompt at bottom

        # calculate the projected extent and pixel size
        # xmin, ymin = t(-180, -85)
        # xmax, ymax = t(180, 85)
        xmin, ymin = t(-170, -55)
        xmax, ymax = t(165, 75)
        pixel_width = (xmax - xmin) / columns
        pixel_height = (ymax - ymin) / lines

        land = "*"
        water = " "


        # stringl=[]
        # os.system('cls' if os.name == 'nt' else 'clear')
        ld=[]
        for line in range(lines):
            for col in range(columns):
                # get the projected x, y of the pixel centroid
                x = xmin + (col + 0.5) * pixel_width
                y = ymax - (line + 0.5) * pixel_height
                # check for a collision

                # self.log((col,line), (x,y),'???')

                objects = [n.object for n in index.intersection((x, y, x, y), objects=True)]
                value=None
                for geom in objects:
                    value = geom.intersects(Point(x, y))
                    if value:
                        d={'x':x,'y':y} #,'col':col,'row':line}
                        ld+=[d]
                        break
                self.stdscr.addstr(line,col,land if value else water)
                self.stdscr.refresh()
                # print(land if value else water, end="")
            # print("")
            # stringl+=['\n']
            df=pd.DataFrame(ld)
            # self.log(df,'!!')
            df['x_norm']=self.do_norm(df['x'])
            df['y_norm']=self.do_norm(df['y'])
            df.to_csv(os.path.join(os.path.dirname(data_fn),'basemap.csv'),index=False)

            # string = ''.join(stringl)
            # print(string)
            
    def do_norm(self,xcol):
        # self.log('<--',xcol)
        minn=xcol.min()
        maxx=xcol.max()
        xcol=pd.Series([x + minn for x in xcol])
        minn=xcol.min()
        maxx=xcol.max()
        res = [(x - minn) / (maxx - minn) for x in xcol]
        # self.log('-->',res)
        return res

    def add_base_map(self):
        # x,y coords
        self.base_df=df=pd.read_csv(os.path.join(os.path.dirname(__file__),'data/basemap.csv'))
        # self.log(df)

        # convert to screen,coords
        coords = {
            (
                int(x*self.width),
                int(y*self.height)
            )
            for x,y in zip(df.x_norm,df.y_norm)
        }
        # self.log(coords)
        # stop

        for row in range(self.width):
            for line in range(self.height):
                if (row,line) in coords:
                    self.stdscr.addstr(self.height - line,row,BASEMAP_MARKER)
                    self.stdscr.refresh()
        # self.stdscr.getch()

    def run_print_map(self,places=[],labels=False,msg=[],offset_y=0):
        if msg:
            for i,x in enumerate(msg):
                x='--> '+x if i else x
                self.stdscr.addstr(i,0,x)
                self.stdscr.refresh()
            self.msg=msg
        if not places: return

        df = self.do_print_map(places) 
        self.log(df,'!?!?!?')
        coords = {
            (
                int(x*self.width),
                int(y*self.height)
            )
            for x,y in zip(df.x_norm,df.y_norm)
        }
        self.log('coords:',coords)
        
        for x,y in coords:
            # lines?
            self.log('xy:',x,y,self.last_coords)
            if self.last_coords:
                lx,ly=self.last_coords
                went_north = bool(ly-y)
                went_east = bool(lx-x)
                
                self.log(f'{lx} -> {x} (x); {ly} -> {y} (y)')
                self.log(f'went east? {went_east}; went north? {went_north}')

                path_x = list(range(lx if lx<x else x, (lx if lx>x else x)+1))
                path_y = list(range(ly if ly<y else y, (ly if ly>y else y)+1))

                if lx>x: path_x.reverse()
                if ly>y: path_y.reverse()

                self.log('path_x:',path_x)
                self.log('path_y:',path_y)
                minlen=min(len(path_x), len(path_y))

                hops_x = slice(path_x,minlen)
                hops_y = slice(path_y,minlen)
                lcoord_x=None
                lcoord_y=None
                for hop_x,hop_y in zip(hops_x,hops_y):
                    self.log('hop_x',hop_x)
                    self.log('hop_y',hop_y)
                    hopmaxlen=max([len(hop_x),len(hop_y)])
                    
                    hopcoords=[]
                    for hi in range(hopmaxlen):
                        hx=hop_x[hi] if hi<len(hop_x) else hop_x[-1]
                        hy=hop_y[hi] if hi<len(hop_y) else hop_y[-1]
                        hopcoords+=[(hx,hy)]
                    for xx,yy in hopcoords:
                        ycoord=self.height - yy - offset_y
                        xcoord=xx
                        self.log('!?',xcoord,ycoord,self.stdscr.instr(ycoord, xcoord,1).decode(),PLACE_MARKER)
                        if self.stdscr.instr(ycoord, xcoord, 1).decode() != PLACE_MARKER:
                            self.stdscr.addstr(ycoord,xcoord,PATH_MARKER)
                            self.stdscr.refresh()
                            time.sleep(0.01)
                        lcoord_x=xx
                        lcoord_y=yy

            self.last_coords=(x,y)
            self.stdscr.addstr(self.height - y - offset_y,x,PLACE_MARKER)
            self.stdscr.refresh()
            time.sleep(.1)





    def endwin(self):
        # time.sleep(1)
        curses.endwin()


    def do_print_map(self,places):
        normed = []
        import utm
        for place,(lat,long) in places:# .items():
            wgs84 = pyproj.Proj(init="EPSG:4326")
            webmerc = pyproj.Proj(proj="webmerc")
            x, y = pyproj.transform(wgs84, webmerc, long, lat)
            # x,y,_,_ = utm.from_latlon(lat,long)
            norm = {'place':place,'lat':lat,'long':long,'x':x,'y':y}
            normed.append(norm)
            self.log('norm:',norm)

        import pandas as pd
        df=pd.DataFrame(normed)#.dropna()
        df=df.append(self.base_df).fillna('') # add basemap!
        df=df[['place','x','y']]
        self.log(df,'with basemap')
        df=df[~df.isin([np.nan, np.inf, -np.inf]).any(1)]
        # self.log('normed',df)
        
            

        df['x_norm'] = self.do_norm(df.x)
        df['y_norm'] = self.do_norm(df.y) 
        # self.log('NORMED\n',df)
        self.log('nas dropped',df)
        return df[df.place!='']


def make_map():
    return curses.wrapper(make_map_curses)

def make_map_curses(stdscr):
    curses.use_default_colors()
    map = Map(stdscr)
    return map


def slice(l,num_slices=None,slice_length=None,runts=True,random=False):
	"""
	Returns a new list of n evenly-sized segments of the original list
	"""
	if random:
		import random
		random.shuffle(l)
	if not num_slices and not slice_length: return l
	if not slice_length: slice_length=int(len(l)/num_slices)
	newlist=[l[i:i+slice_length] for i in range(0, len(l), slice_length)]
	if runts: return newlist
	return [lx for lx in newlist if len(lx)==slice_length]



if __name__ == '__main__':
    try:
        map=make_map()
        map.precompute_basemap()
        # map.add_base_map()
    except KeyboardInterrupt:
        map.endwin()


