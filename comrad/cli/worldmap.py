# Code from 
# https://github.com/snorfalorpagus/ascii-world-map


import json
from functools import partial
from shutil import get_terminal_size
from shapely.geometry import shape, Point
from shapely import ops
import pyproj,math,os
import rtree


import warnings
warnings.filterwarnings(action='ignore')



# read the data into a list of shapely geometries
with open("data/world-countries2.json") as f:
    data = json.load(f)



def print_map(countries=[]):

    geoms_all = [
        shape(feature["geometry"])
        for feature in data["features"]
    ]

    geoms = [
        shape(feature["geometry"])
        for feature in data["features"]
        if not countries or feature.get('properties',{}).get('name',None) in countries
    ]

    # transform the geometries into web mercator
    wgs84 = pyproj.Proj(init="EPSG:4326")
    webmerc = pyproj.Proj(proj="webmerc")
    t = partial(pyproj.transform, wgs84, webmerc)
    geoms = [ops.transform(t, geom) for geom in geoms]
    geoms_all = [ops.transform(t, geom) for geom in geoms_all]

    # create a spatial index of the geometries
    def gen(geoms):
        for n, geom in enumerate(geoms):
            yield n, geom.bounds, geom
    index = rtree.index.Index(gen(geoms))
    index_all = rtree.index.Index(gen(geoms_all))



    # get the window size
    size = get_terminal_size(fallback=(80, 24))
    columns = size.columns
    lines = size.lines - 1 - 3  # allow for prompt at bottom

    # calculate the projected extent and pixel size
    # xmin, ymin = t(-180, -85)
    # xmax, ymax = t(180, 85)
    xmin, ymin = t(-180, -62)
    xmax, ymax = t(180, 79)
    pixel_width = (xmax - xmin) / columns
    pixel_height = (ymax - ymin) / lines

    land = "*"
    water = " "
    highlight='█'


    # stringl=[]
    # os.system('cls' if os.name == 'nt' else 'clear')
    for line in range(lines):
        for col in range(columns):
            # get the projected x, y of the pixel centroid
            x = xmin + (col + 0.5) * pixel_width
            y = ymax - (line + 0.5) * pixel_height
            # check for a collision
            objects = [n.object for n in index.intersection((x, y, x, y), objects=True)]
            
            value = False
            done=False
            for geom in objects:
                value = geom.intersects(Point(x, y))
                if value:
                    print(highlight,end="")
                    # stringl+=[highlight]
                    done=True
                    break
            
            if not done:
                objects = [n.object for n in index_all.intersection((x, y, x, y), objects=True)]
                for geom in objects:
                    value = geom.intersects(Point(x, y))
                    if value:
                        break
                print(land if value else water, end="")
                # stringl+=[land if value else water]
        print("")
        # stringl+=['\n']

        # string = ''.join(stringl)
        # print(string)

places = {
    'Cambridge':(52.205338,0.121817),
    'Sydney':(-33.868820,151.209290),
    'New York':(40.712776,-74.005974),
    'Hong Kong':(22.278300,114.174700),
    'Cape Town':(33.9249, 18.4241),
    'San Francisco':(-12.125640,-77.018967),
}

places_utm = {
    'Honolulu':(618431.58,2357505.97),
    'Tokyo':(394946.08,3946063.75),
    'Ushuaia':(544808.23,3927028.51),
    'Reykjavik':(459698.38,7111571.73)
}


def print_map_simple(places):
    size = get_terminal_size(fallback=(80, 24))
    columns = size.columns
    lines = size.lines - 1 - 3  # allow for prompt at bottom

    # calculate the projected extent and pixel size
    # xmin, ymin = (-180, -85)
    # xmax, ymax = (180, 85)
    # pixel_width = (xmax - xmin) / columns
    # pixel_height = (ymax - ymin) / lines

    long_min,long_max = -180,180
    # lat_min,lat_max = -85,85
    lat_min,lat_max = -75,80


    # utm_easting_min = 166640
    # utm_easting_max = 833360
    # utm_northing_min = 1110400
    # utm_northing_max = 9334080
    utm_easting_min = places_utm['Honolulu'][0]
    utm_easting_max = places_utm['Tokyo'][0]
    utm_northing_min = places_utm['Ushuaia'][1]
    utm_northing_max = places_utm['Reykjavik'][1]

    # import pyproj as proj

    # setup your projections
    # crs_wgs = proj.Proj(init='epsg:4326') # assuming you're using WGS84 geographic
    # crs_bng = proj.Proj(init='epsg:27700') # use a locally appropriate projected CRS


    import utm

    normed = {}
    for place,(lat,long) in places.items():
        # wgs84 = pyproj.Proj(init="EPSG:4326")
        # webmerc = pyproj.Proj(proj="webmerc")
        # x, y = proj.transform(wgs84, webmerc, long, lat)
        


        longx = (long - long_min) / (long_max - long_min)
        laty = (lat - lat_min) / (lat_max - lat_min)

        utm_easting,utm_northing,utm_zone_num,utm_zone_letter = utm.from_latlon(lat,long)
        
        utmx = (utm_easting - utm_easting_min) / (utm_easting_max - utm_easting_min)
        utmy = (utm_northing - utm_northing_min) / (utm_northing_max - utm_northing_min)


        # norm = ( int(longx*columns), int(laty*lines) )
        norm = ( int(utmx*columns), int(utmy*lines) )
        # print(place,(utm_easting,utm_northing),(utmx,utmy),norm)

        norm = (norm[0], lines - norm[1])

        normed[norm] = place

    p_i=None
    place_now=None
    for line in range(lines):
        for col in range(columns):
            if (col,line) in normed:
                print('*',end="")
                place=normed[(col,line)]
                place_now=place
                p_i=0
            elif p_i is not None:
                try:
                    print(place_now[p_i],end="")
                    p_i+=1
                except IndexError:
                    place_now=None
                    p_i=None
            else:
                print(" ",end="")
    print()


if __name__ == '__main__':
    print_map() #['Brazil','Netherlands','Thailand'])
    # print_map_simple(places)