#!/usr/bin/env sh

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
    git fetch bb > /dev/null
    git branch --set-upstream master bb/master
    git merge bb/master --ff-only
    popd > /dev/null 
  else
    ./git_install.sh "$clone" "$dir"
  fi

}


_install "notes" "$HOME/.gtd"

mkdir -p "$HOME/.ovpn"
_install "ovpn" "$HOME/.ovpn/ovpn"

