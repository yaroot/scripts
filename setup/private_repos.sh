#!/usr/bin/env bash

_install() {
  local repo="$1"
  local dir="$2"
  local clone="git@bitbucket.org:yaroot/${repo}.git"

  if [ -d "$dir" ]; then
    pushd "$dir" > /dev/null
    for remote in `git remote`; do
      git remote rm $remote
    done
    git remote add bb "$clone"
    git fetch bb
    git branch --set-upstream master bb/master
    popd > /dev/null
  fi

  ./git_install.sh "$clone" "$dir"
}


_install "notes" "$HOME/.gtd"

if [ 'Darwin' = `uname -s` ]; then
  _install "ovpn" "$HOME/.ovpn"
else
  mkdir -p "$HOME/.ovpn"
  _install "ovpn" "$HOME/.ovpn/.ovpn"
fi

