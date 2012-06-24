#!/usr/bin/env bash

protocol='git'
if [ "x${1}" = 'x--ssh' ]; then
  protocol='ssh'
fi

_install() {
  local repo="$1"
  local dir="$2"
  if [ "$protocol" == 'ssh' ]; then
    repo="git@github.com:${repo}.git"
  else
    repo="git://github.com/${repo}.git"
  fi

  ./git_install.sh "$repo" "$dir"
}

_install "yaroot/dotfiles" "$HOME/.dotfiles"
_install "yaroot/scripts" "$HOME/.bin"
_install "yaroot/vimrc" "$HOME/.vim"

which emacs 2>&1 > /dev/null && _install "yaroot/emacsd" "$HOME/.emacs.d"
which irssi 2>&1 > /dev/null && _install "yaroot/dotirssi" "$HOME/.irssi/scripts/autorun"


