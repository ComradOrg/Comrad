#!/bin/bash
#
# Usage: curl https://pyenv.run | bash
#
# For more info, visit: https://raw.githubusercontent.com/pyenv/pyenv-installer
#
index_main() {
    set -e
    curl -s -S -L https://github.com/Komrade/Komrade/blob/master/script/komrade-installer.py | bash
}

index_main