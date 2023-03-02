#!/usr/bin/env bash


mkdir -p $HOME/.local/bin
mkdir -p $HOME/.mnt
# mkdir -p $HOME/.mnt/private

use_ssh=true
# if [ '-n' = "${1}" ]; then
#   use_ssh=false
# fi
while getopts "n" opt; do
  case $opt in
    n)
      use_ssh=false
  esac
done

echo "SSH protocol: $use_ssh"

_install() {
  local repo="$1"
  local dir="$2"
  if $use_ssh; then
    repo="git@github.com:${repo}.git"
  else
    repo="https://github.com/${repo}.git"
  fi

  if $use_ssh; then
    if [ -d "$dir/.git" ]; then
      pushd "$dir" > /dev/null
      git remote set-url origin $repo
      popd > /dev/null
    fi
  fi

  ./git_install.sh "$repo" "$dir"
}

_install "yaroot/dotfiles" "$HOME/.dotfiles"
_install "yaroot/scripts" "$HOME/.bin"
_install "yaroot/vimrc" "$HOME/.vim"

if [ -f '/etc/os-release' ]; then
  source '/etc/os-release'
  if [ "$NAME" = 'Arch Linux' ]; then
    if [ -z `which auracle` ]; then
      # http://github.com/falconindy/cower
      wget https://aur.archlinux.org/cgit/aur.git/snapshot/auracle-git.tar.gz
    fi
  fi
fi

# https://git.grml.org/f/grml-etc-core/etc/zsh/zshrc
