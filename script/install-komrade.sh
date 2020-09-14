#!/bin/bash
#
# Usage: curl https://pyenv.run | bash
#
# For more info, visit: https://raw.githubusercontent.com/pyenv/pyenv-installer
#
index_main() {
    set -e
    curl https://raw.githubusercontent.com/Komrade/Komrade/master/script/komrade-installer.py | python -
}

index_main