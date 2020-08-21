DEFAULT_SCREEN='profile'

import random
HORIZONTAL = False #random.choice([True,True,True,False])
FACTOR=1
WINDOW_SIZE = (1136*FACTOR,640*FACTOR) if HORIZONTAL else (640*FACTOR,1136*FACTOR)



WINDOW_SIZE=700,700

BG_IMG='assets/bg-brown.png'

grass=(201,203,163)
russiangreen = (109,140,96)
huntergreen = (67,92,61)
kombugreen = (49,67,45)
pinetreegreen = (29,40,27)
junglegreen = (15, 21, 14)

browncoffee=(77, 42, 34)
rootbeer=(38, 7, 1)
blackbean=(61, 12, 2)
burntumber=(132, 55, 34)
brownsugar=(175, 110, 81)
antiquebrass= (198, 144, 118)
royalbrown=(94, 55, 46)
bole=(113, 65, 55)
liver= (110, 56, 31)
bistre=(58, 33, 14)
bistre2=(43, 21, 7)
skin1=(89, 47, 42)
skin2=(80, 51, 53)
skin3=(40, 24, 26)

grullo=177, 158, 141
smokyblack=33, 14, 0
liverchestnut=148, 120, 96
ashgray=196, 199, 188
livchestnut2=156, 106, 73
beaver=165, 134, 110
rawumber=120, 95, 74

persianred=202,52,51
vermillion=126,25,27
indianred=205,92,92
barnred=124,10,2
maroon=128,0,0
bloodred=98, 23, 8
rust=188, 57, 8
darksienna=34, 9, 1
yellowcrayola=246, 170, 28
darkred=148, 27, 12
rosewood=94, 11, 21
redviolet=144, 50, 61
bone=217, 202, 179
bronze=188, 128, 52
shadow=140, 122, 107
orangered=194, 3, 3
  
dutchwhite=229,219,181
# black=(0,0,0)
black=15, 15, 15 #5, 8, 13

eerieblack=23, 22, 20
bistre=58, 38, 24
tuscanred=117, 64, 67
grullo2=154, 136, 115
blackolive=55, 66, 61


dogreen=103, 116, 35
sage=187, 193, 145
alabaster2 = 241, 236, 226
coyotebrown = 138, 93, 61
vandykebrown = 90, 62, 41

darksienna2=55, 6, 23
xiketic=3, 7, 30

rossacorsa=208, 0, 0
raisinblack=38, 34, 34
coffee2=67, 58, 58
rufusred=171, 4, 4
darksienna3=56, 22, 13


black2=0, 20, 39
xanadu=112, 141, 129
jasmine=244, 213, 141
ioe=191, 6, 3
dred=141, 8, 1
caputmort1=74, 36, 25


# SCHEME = 'lgreen'
# SCHEME = 'bronze'
SCHEME = 'dark'



# light green theme?
if SCHEME=='lgreen':
    COLOR_TOOLBAR= huntergreen #bone #smokyblack #5,5,5 #russiangreen #pinetreegreen #kombugreen #(12,5,5) #russiangreen
    COLOR_BG = grass # russiangreen #(0,73,54)
    COLOR_LOGO = coyotebrown # grass#russiangreen #(0,0,0) #(0,0,0) #(151,177,140) #(132,162,118) #(109,140,106)
    COLOR_TEXT = black #(255,245,200) #(0,0,0,1) #(241,233,203) #COLOR_ICON #(207,219,204) #(239,235,206) # (194,211,187) # (171,189,163) # (222,224,198) # COLOR_LOGO #(223, 223, 212)
    COLOR_CARD = bone   #(67,92,61) #(12,9,10)
    COLOR_CARD_BORDER = COLOR_CARD
    COLOR_ICON=COLOR_LOGO

elif SCHEME=='bronze':        
    COLOR_TOOLBAR= junglegreen
    COLOR_BG = bronze
    COLOR_LOGO = rufusred #yellowcrayola #0,0,0
    COLOR_TEXT = black
    COLOR_CARD = bone
    COLOR_CARD_BORDER = COLOR_CARD
    COLOR_ICON=COLOR_LOGO

else:
    # COLOR_TOOLBAR= black
    # COLOR_TOOLBAR=bronze
    # COLOR_LOGO = black #bronze #0,0,0
    

    # COLOR_BG = black
    COLOR_BG=bistre
    COLOR_TOOLBAR=black
    COLOR_LOGO=bronze
    COLOR_TEXT = black
    COLOR_CARD = bone
    COLOR_CARD_BORDER = COLOR_CARD
    COLOR_ICON=COLOR_LOGO
    COLOR_ACCENT = huntergreen

