# addresses
COMRAD_ONION = 'comradxfmyuf2ntu.onion' #u7spnj3dmwumzoa4.onion'
COMRAD_ONION2 = 'rwg4zcnpwshv4laq.onion'
COMRAD_URL = 'komrade.dev'  #COMRAD_ONION


OPERATOR_API_URL_TOR = f'http://{COMRAD_ONION}/op/'
OPERATOR_API_URL_CLEARNET = f'http://{COMRAD_URL}/op/'

OPERATOR_API_URL = OPERATOR_API_URL_TOR

# paths
import os
PATH_USER_HOME = os.path.join(os.path.expanduser('~'))
PATH_COMRAD = os.path.abspath(os.path.join(os.path.expanduser('~'),'comrad','data'))
PATH_COMRAD_KEYS = os.path.join(PATH_COMRAD,'.keys')
PATH_COMRAD_DATA = os.path.join(PATH_COMRAD,'.data')
PATH_COMRAD_LIB = os.path.abspath(os.path.join(os.path.expanduser('~'),'comrad','lib'))

PATH_CRYPT_OP_KEYS = os.path.join(PATH_COMRAD_KEYS,'.op.db.keys.crypt')
PATH_CRYPT_OP_DATA = os.path.join(PATH_COMRAD_DATA,'.op.db.data.crypt')

# PATH_CRYPT_CA_KEYS = os.path.join(PATH_COMRAD_KEYS,'.ca.db.keys.crypt')
# PATH_CRYPT_CA_DATA = os.path.join(PATH_COMRAD_DATA,'.ca.db.data.encr')
PATH_CRYPT_CA_KEYS = PATH_CRYPT_OP_KEYS
PATH_CRYPT_CA_DATA = PATH_CRYPT_OP_DATA
PATH_QRCODES = os.path.join(PATH_COMRAD,'contacts')
# PATH_SECRETS = os.path.join(PATH_COMRAD,'.secrets')
PATH_SECRETS = PATH_SUPER_SECRETS = os.path.join(PATH_USER_HOME,'.secrets')
PATH_SUPER_SECRET_OP_KEY = os.path.join(PATH_SUPER_SECRETS,'.comrad.op.key')

PATH_MAPS = os.path.join(PATH_COMRAD,'maps')

PATH_LOG_OUTPUT = os.path.join(PATH_COMRAD,'logs')
PATH_AVATARS = os.path.join(PATH_COMRAD,'avatars')


for x in [PATH_COMRAD,PATH_COMRAD_DATA,PATH_COMRAD_KEYS,PATH_QRCODES,PATH_SECRETS,PATH_SUPER_SECRETS,PATH_LOG_OUTPUT,PATH_AVATARS]:
    if not os.path.exists(x):
        os.makedirs(x)

CRYPT_USE_SECRET = True
PATH_CRYPT_SECRET = os.path.join(PATH_SECRETS,'.salt')
PATH_CRYPT_SECRET_KEY = os.path.join(PATH_SECRETS,'.key')
AVATAR_WIDTH=300


# etc
BSEP=b'||||||||||'
BSEP2=b'@@@@@@@@@@'
BSEP3=b'##########'

OPERATOR_NAME = 'Operator'
TELEPHONE_NAME = 'Telephone'
WORLD_NAME = 'comrades'
PATH_REPO = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..'
    )
)
PATH_GUI = os.path.join(PATH_REPO,'comrad','app')
PATH_GUI_ASSETS = os.path.join(PATH_GUI,'assets')
PATH_DEFAULT_AVATAR = os.path.join(PATH_GUI_ASSETS,'avatars','britney2.jpg')

PATH_REPO = PATH_APP = os.path.abspath(os.path.dirname(__file__))
# PATH_APP = os.path.join(PATH_REPO,'comrad')
# PATH_BUILTIN_KEYCHAINS_ENCR = os.path.join(PATH_APP,'.builtin.keychains.encr')
PATH_BUILTIN_KEYCHAIN = os.path.join(PATH_APP,'.builtin.keys')
PATH_OMEGA_KEY = os.path.join(PATH_APP,'.omega.key')
# PATH_BUILTIN_KEYCHAINS_DECR = os.path.join(PATH_APP,'.builtin.keychains.decr')
PATH_GUI = os.path.join(PATH_APP, )

# key names

KEYNAMES = [
    'pubkey','privkey','adminkey',
    'pubkey_encr','privkey_encr','adminkey_encr',
    'pubkey_decr','privkey_decr','adminkey_decr',
    'pubkey_encr_encr','privkey_encr_encr','adminkey_encr_encr',
    'pubkey_encr_decr','privkey_encr_decr','adminkey_encr_decr',
    'pubkey_decr_encr','privkey_decr_encr','adminkey_decr_encr',
    'pubkey_decr_decr','privkey_decr_decr','adminkey_decr_decr'
]

OPERATOR_INTERCEPT_MESSAGE = "If you'd like to make a call, please hang up and try again. If you need help, hang up, and then dial your operator."

ALLOWED_IMG_EXT = {'png','jpg','jpeg','gif'}

# KEYMAKER_DEFAULT_KEYS_TO_SAVE = ['pubkey_encr', 'privkey_encr', 'adminkey_encr']
# KEYMAKER_DEFAULT_KEYS_TO_RETURN =  ['pubkey_decr_encr', 'privkey_decr_encr', 'adminkey_decr_encr']


# defaults oriented to Callers

# kept on server
KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_SERVER = ['pubkey']   # stored under QR URI

# kept on client
KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_CLIENT = ['privkey_encr','privkey_decr']
                                   #'pubkey'  # as QR
                                #    'privkey_encr',  
                                #    'adminkey_encr',
                                #    'privkey_decr'],
                                   #'privkey_decr_encr',
                                   #'privkey_decr_decr',
                                #    'adminkey_decr_encr',
                                #    'adminkey_decr_decr']

# KEYMAKER_DEFAULT_KEYS_TO_GEN =  ['pubkey','privkey','adminkey',
                                #  'pubkey_decr','privkey_decr', 'adminkey_decr']
KEYMAKER_DEFAULT_KEYS_TO_GEN = ['pubkey','privkey']
KEYMAKER_DEFAULT_KEYS_TO_GEN += KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_SERVER
KEYMAKER_DEFAULT_KEYS_TO_GEN += KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_CLIENT
KEYMAKER_DEFAULT_KEYS_TO_GEN = list(set(KEYMAKER_DEFAULT_KEYS_TO_GEN))
KEYMAKER_DEFAULT_KEYS_TO_GEN.sort(key=lambda x: x.count('_'))

# print('KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_SERVER',KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_SERVER)
# print('KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_CLIENT',KEYMAKER_DEFAULT_KEYS_TO_SAVE_ON_CLIENT)
# print('KEYMAKER_DEFAULT_KEYS_TO_GEN',KEYMAKER_DEFAULT_KEYS_TO_GEN)


KEY_TYPE_ASYMMETRIC_PUBKEY = 'asymmetric_pubkey'
KEY_TYPE_ASYMMETRIC_PRIVKEY = 'asymmetric_privkey'
KEY_TYPE_SYMMETRIC_WITHOUT_PASSPHRASE = 'symmetric_key_without_passphrase'
KEY_TYPE_SYMMETRIC_WITH_PASSPHRASE = 'symmetric_key_with_passphrase'
ENCRYPTED_KEY = 'encrypted_key'




KEYMAKER_DEFAULT_ALL_KEY_NAMES = KEYNAMES

WHY_MSG = 'password: '#What is the password of memory for this account? '



TELEPHONE_KEYCHAIN = None
OPERATOR_KEYCHAIN = None
WORLD_KEYCHAIN = None
OMEGA_KEY = None
OPERATOR = None
TELEPHONE = None




PATH_OPERATOR_WEB_KEYS_FILE = f'/home/ryan/www/website-komrade/pub'
PATH_OPERATOR_WEB_KEYS_URL = f'http://{COMRAD_URL}/pub'
# PATH_OPERATOR_WEB_CONTACT_OP_URL = f'http://{COMRAD_URL}/.contacts/TheOperator.png'
# PATH_OPERATOR_WEB_CONTACT_PH_URL = f'http://{COMRAD_URL}/.contacts/TheTelephone.png'


# dangerous! leave on only if absolutely necessary for initial dev
ALLOW_CLEARNET = True


DEBUG_DEFAULT_PASSPHRASE = None # 'all your base are belong to us'


ROUTE_KEYNAME = 'request'


OPERATOR_INTRO = 'Hello, this is the Operator speaking. '




VISIBILITY_TYPE_PUBLIC = 'VISIBILITY_TYPE_PUBLIC'  # visible to the world
VISIBILITY_TYPE_SEMIPUBLIC = 'VISIBILITY_TYPE_SEMIPUBLIC'  # visible to the world
VISIBILITY_TYPE_PRIVATE = 'VISIBILITY_TYPE_PRIVATE'  # visible to the world

DEFAULT_USER_SETTINGS = {
    'visibility':VISIBILITY_TYPE_SEMIPUBLIC
}

import os
SHOW_LOG = 1
SHOW_STATUS = 0
PAUSE_LOGGER = 0
CLEAR_LOGGER = 0

SAVE_LOGS = 1

CLI_TITLE = 'COMRAD'
CLI_FONT = 'clr5x6'#'colossal'
CLI_WIDTH = STATUS_LINE_WIDTH = 60
CLI_HEIGHT = 30


MAX_POST_LEN = 1000
MAX_MSG_LEN = 1000


import os,logging
if not 'COMRAD_SHOW_LOG' in os.environ or not os.environ['COMRAD_SHOW_LOG'] or os.environ['COMRAD_SHOW_LOG']=='0':
    logger = logging.getLogger()
    logger.propagate = False

if not 'COMRAD_USE_TOR' in os.environ or not os.environ['COMRAD_USE_TOR']:
    COMRAD_USE_TOR = os.environ['COMRAD_USE_TOR'] = '1'
if not 'COMRAD_USE_CLEARNET' in os.environ or not os.environ['COMRAD_USE_CLEARNET']:
    COMRAD_USE_CLEARNET = os.environ['COMRAD_USE_CLEARNET'] = '0'



FONT_PATH = os.path.join(PATH_GUI_ASSETS,'font.otf')

























#from p2p_api import 
PORT_LISTEN = 5969

# NODES_PRIME = [("128.232.229.63",8467), ("68.66.241.111",8467)] 
NODES_PRIME = [("128.232.229.63",8467)] 








  


DEFAULT_URI='/login/'

import random,platform
HORIZONTAL = True # random.choice([True,True,True,False])
FACTOR=1
WINDOW_SIZE = (1136*FACTOR,640*FACTOR) if HORIZONTAL else (640*FACTOR,1136*FACTOR)


PLAYING_CARDS = (2.5,3.5)
ASPECT_RATIO = PLAYING_CARDS[0]/PLAYING_CARDS[1]
ASPECT_RATIO = 1/ASPECT_RATIO
HEIGHT = 850

if platform.platform().startswith('Linux'):
    HEIGHT *= 1.25


WINDOW_SIZE=int(HEIGHT),int(HEIGHT * ASPECT_RATIO)

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


COLOR_INACTIVE = COLOR_CARD
COLOR_ACTIVE = russiangreen


ALL_COLORS = list({v for (k,v) in globals().items() if type(v)==tuple and len(v)==3})



SCREEN_TO_ICON = {
    'feed':'home-outline',
    'messages':'message-outline',
    'post':'pencil-plus-outline',
    'profile':'account-circle-outline',
    'refresh':'refresh',
    'login':'exit-run'
}