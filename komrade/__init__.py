###
# Define some basic things while we're here

class KomradeException(Exception): pass

# make sure komrade is on path
import sys,os
sys.path.append(os.path.dirname(__file__))

import inspect
class Logger(object):
    def log(self,*x):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        mytype = type(self).__name__
        caller = calframe[1][3]
        print(f'\n[{mytype}.{caller}()]',*x)
