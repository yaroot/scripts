#!/usr/bin/env bash

PACAPT_DIR="$HOME/repos/pacapt"
./git_install.sh git://github.com/icy/pacapt.git $PACAPT_DIR


if [ -f "/etc/os-release" ]; then
  source /etc/os-release
  if [ $ID = 'arch' ]; then
    echo "Error: you're running archlinux :)"
    exit 0
  fi
fi

cd /usr/bin; sudo ln -sv "${PACAPT_DIR}/pacapt/pacman" .


