import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
# from komrade import *

import sys
port = '8080' if len(sys.argv)<2 or not sys.argv[1].isdigit() else sys.argv[1]




from switchboard import run_forever
run_forever(port = port)