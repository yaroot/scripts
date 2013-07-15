#!/usr/bin/env sh


mkdir -p $HOME/.local/bin
mkdir -p $HOME/.mnt
# mkdir -p $HOME/.mnt/private


use_ssh=false
if [ '--ssh' = "${1}" ]; then
  use_ssh=true
fi

_install() {
  local repo="$1"
  local dir="$2"
  if $use_ssh; then
    repo="git@github.com:${repo}.git"
  else
    repo="git://github.com/${repo}.git"
  fi

  ./git_install.sh "$repo" "$dir"
}

_install "yaroot/dotfiles" "$HOME/.dotfiles"
_install "yaroot/scripts" "$HOME/.bin"
_install "yaroot/vimrc" "$HOME/.vim"

which irssi &> /dev/null && _install "yaroot/dotirssi" "$HOME/.irssi/scripts/autorun"

_install yaroot/spiped-PKGBUILD $HOME/repos/spiped-PKGBUILD
_install yaroot/tabbed-PKGBUILD $HOME/repos/tabbed-PKGBUILD
_install yaroot/shadowsocks-go-PKGBUILD $HOME/repos/shadowsocks-go-PKGBUILD
_install yaroot/network.sh $HOME/repos/network.sh


EMACS=`which emacs 2> /dev/null`
JOVE=`which jove 2> /dev/null`
if [ -n "$EMACS" ]; then
  has_emacs=true
  # debian has jove as emacs
  if [ -n "$JOVE" ]; then
    if [ "`readlink -fn $EMACS`" = "$JOVE" ]; then
      has_emacs=false
    fi
  fi

  if $has_emacs; then
    _install "yaroot/emacsd" "$HOME/.emacs.d"
  fi
fi

if [ -f '/etc/os-release' ]; then
  source '/etc/os-release'
  if [ "$NAME" = 'Arch Linux' ]; then
    if [ -z `which cower` ]; then
      # http://github.com/falconindy/cower
      wget http://aur.archlinux.org/packages/co/cower/cower.tar.gz
    fi
  fi
fi


