#!/usr/bin/env bash

PACAPT_DIR="$HOME/repos/pacapt"
./git_install.sh git://github.com/icy/pacapt.git $PACAPT_DIR

cd /usr/bin; sudo ln -sv "${PACAPT_DIR}/pacapt/pacman" .


