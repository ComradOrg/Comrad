#!/usr/bin/env python3

URL_PYENV = 'https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer'

import os,sys,urllib,shutil
from urllib import request
import distutils
from distutils import dir_util



print('''
              #  #   ##   #  #  ###    ##   ###   #### 
              # #   #  #  ####  #  #  #  #  #  #  #    
              ##    #  #  ####  ###   #  #  #  #  ###  
              # #   #  #  #  #  # #   ####  #  #  #    
              #  #   ##   #  #  #  #  #  #  ###   #### 
                                          

installing...
''')

PATH_HOME = os.path.expanduser('~')
PATH_KOMRADE = os.path.join(PATH_HOME,'komrade')
path_pyenv = os.path.join(PATH_HOME,'.pyenv')
path_repo = os.path.join(PATH_KOMRADE,'code')
def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    return which(name) is not None


def main():

    # 1) get path
    path_komrade = input('Path to save komrade to:\n['+PATH_KOMRADE+'] ').strip()
    path_komrade = PATH_KOMRADE if not path_komrade else path_komrade
    if not os.path.exists(path_komrade): os.makedirs(path_komrade)
    os.chdir(path_komrade)

    # 2) install pyenv?
    if not os.path.exists(path_pyenv):
        pyenv_yn = input('\npyenv is not installed. Install?\n[Y/n] ').strip().lower()
        if pyenv_yn != 'n':
            print('installing pyenv...')
            os.system('curl https://pyenv.run | bash')

    # # 3) download komrade
    print('\ndownloading Komrade...')
    if is_tool('git'):
        if os.path.exists(path_repo):
            os.chdir(path_repo)
            os.system('git pull')
        else:
            os.chdir(path_komrade)
            os.system('git clone https://github.com/Komrade/Komrade.git')
    else:
        os.chdir(path_komrade)
        request.urlretrieve(
            'https://github.com/Komrade/Komrade/archive/master.zip',
            'komrade-github.zip'
        )
        os.system('unzip -o komrade-github.zip')
        distutils.dir_util.copy_tree("Komrade-master", "code")
    
        shutil.rmtree('Komrade-master')
        os.remove('komrade-github.zip')

    ## 4) install komrade
    os.chdir(path_repo)
    os.environ['PYENV_ROOT']=path_pyenv
    os.environ['PATH'] = os.path.join(path_pyenv,'bin') + os.environ['PATH']
    # os.system('. script/bootstrap')
    os.system('''

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

echo `which pyenv`

#if command -v pyenv 1>/dev/null 2>&1; then
# eval "$(pyenv init -)"
#fi  
    

. script/bootstrap

''')


main()