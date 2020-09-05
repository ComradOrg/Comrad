import sys
port = '8080' if len(sys.argv)<2 or not sys.argv[1].isdigit() else sys.argv[1]
from operators import run_forever; run_forever(port = port)