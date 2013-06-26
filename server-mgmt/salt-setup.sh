#!/usr/bin/env bash

setup_pacman() {
  pacman -Syy
  pacman -Su --noconfirm --ignore bash,firesystem
  pacman -S --noconfirm bash
  pacman -S --noconfirm firesystem

  pacman -Scc

  if [ ! `grep '\[salt\]' /etc/pacman.conf` ]; then
    echo '' >> /etc/pacman.conf
    echo '' >> /etc/pacman.conf
    echo '[salt]' >> /etc/pacman.conf
    echo 'SigLevel = Never' >> /etc/pacman.conf
    echo 'Server = http://yaroot.net/files/salt-archlinux/$arch' >> /etc/pacman.conf
    echo '' >> /etc/pacman.conf
    echo '' >> /etc/pacman.conf
  fi

  pacman -Sy --noconfirm salt
}



main() {
  source /etc/os-release
  if [ $ID = 'arch' ]; then
    setup_pacman
  fi
}
