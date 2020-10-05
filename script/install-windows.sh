#!/bin/bash


# install pyenv?

echo "
                 ###   ##   #  #  ###    ##   ###                
                #     #  #  ####  #  #  #  #  #  #               
                #     #  #  ####  ###   #  #  #  #               
                #     #  #  #  #  # #   ####  #  #               
                 ###   ##   #  #  #  #  #  #  ###                

                                                           
installing...

"            


###
# Create paths
######


echo '
1) setting up folders...

'
# install dir?
echo "Where should comrad live on your device?"
path_comrad_default="`realpath ~/comrad`"

if [ "$1" = "-n" ]
then
    read -p "[$path_comrad_default] " path_comrad
else
    path_comrad=$path_comrad_default
fi


if [ -z "$path_comrad" ]
then
    path_comrad=$path_comrad_default
fi

if [ ! -d "$path_comrad" ]
then
    mkdir -p $path_comrad
    echo "created $path_comrad"
fi

path_lib="$path_comrad/lib"
if [ ! -d "$path_lib" ]
then
    mkdir -p $path_lib
    echo "created $path_lib"
fi
   

path_repo="$path_comrad/code"
path_bin="$path_repo/bin"




echo '
2) configuring OS environment...

'



#### 
# Package manager setups
# 
pacman -S --needed curl wget unzip gcc make openssl-devel git libcrypt-devel python3 python3-pip mingw-w64-x86_64-python3-pandas python-devel mingw-w64-x86_64-python3-numpy mingw-w64-x86_64-python3-pep517 mingw-w64-x86_64-libjpeg-turbo mingw-w64-x86_64-python3-pillow mingw-w64-x86_64-zbar








### Downloading via git!

echo '

2) downloading Comrad...

'
# if exists, pull
if [ -d "$path_repo" ]
then 
    cd $path_repo
    git pull
else
    cd $path_comrad
    git clone https://github.com/ComradOrg/Comrad.git
    mv Comrad code
fi








############################################################


echo '

5) creating virtual environment...

'
path_venv="$path_repo/venv"
echo "Now using python (t1): `which python`"
python -m pip install -U setuptools pip wheel

# python -m pip install virtualenv

python -m venv "$path_venv"
source "$path_venv/bin/activate"

echo "Now using python (t2): `which python`"
python -m pip install -U setuptools pip wheel




###########################################################

echo '

Install python requirements

'

cd $path_repo
python -m pip install --prefer-binary -r requirements.txt





exit 1
#############################################################

# echo '
# Installing other requirements

# Rlite, hardware based redis database

# '

# cd $path_lib
# git clone https://github.com/seppo0010/rlite.git
# cd rlite
# make
# make all



# exit 1



#########################################################################

if [ "$machine" = "Mac" ]
then
    echo "Installing Mac native GUI bridge"
    python -m pip install git+https://github.com/kivy/pyobjus
fi


#######################################

echo '

Themis, cryptography backend...

'


if [ "$machine" = "Mac" ]
then
    echo 'installing themis with brew'
    /usr/local/bin/brew tap cossacklabs/tap
    /usr/local/bin/brew install libthemis
else
    if [ ! -f "/usr/local/lib/libthemis.so" ]
    then
        if [ ! -f "/usr/lib/libthemis.so" ]
        then
            echo 'building themis'
            cd "$path_lib"
            # pwd
            #git clone https://github.com/cossacklabs/themis.git
            curl https://codeload.github.com/cossacklabs/themis/zip/master -o themis.zip
            unzip -q -o themis.zip
            #mv themis-master themis
            cd themis-master
            make
            make install
            # sudo make install
        fi
    fi
fi




echo '

Completing...

'

commands_app="
    source $path_conda/etc/profile.d/conda.sh\n
    export PATH=\"$path_conda/bin:\$PATH\"\n
    conda activate $path_venv\n
    python -m pip install -r $path_repo/requirements.txt\n
    python $path_repo/comrad/app/main.py\n
"



export PATH="$path_bin:$PATH"
bashline="export PATH=\"$path_bin:\$PATH\"     # comrad installation"
bashfn="`realpath ~/.bashrc`"

# add to bashrc?
if grep -Fxq "$bashline" "$bashfn"
then
    # code if found
    echo "setting already in $bashfn: $bashline"
else
    # code if not found
    echo "$bashline" >> "$bashfn"
fi


echo -e "Now run Comrad with:

comrad-app    [GUI interface -- alpha]

If that doesn't work, try running this series of comands:

$commands_app

"


if [ "$machine" = "Mac" ]
then
    cd /Applications
    unzip -q -o "$path_bin/Comrad.app.zip"
    echo "You may run the app by looking for 'Comrad.app' in your /Applications folder."
fi














# run?
. $path_bin/comrad-app

