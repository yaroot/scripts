#!/usr/bin/env bash

# n
./git_install.sh git://github.com/visionmedia/n.git $HOME/repos/n
mkdir -p $HOME/.nodes/bin

# rbenv
./git_install.sh git://github.com/sstephenson/rbenv.git $HOME/.rbenv
./git_install.sh git://github.com/sstephenson/ruby-build.git $HOME/.rbenv/plugins/ruby-build
./git_install.sh git://github.com/jamis/rbenv-gemset.git $HOME/.rbenv/plugins/rbenv-gemset

# virtualenv
./git_install.sh git://github.com/pypa/virtualenv.git $HOME/repos/virtualenv

# youtube-dl
./git_install.sh git://github.com/rg3/youtube-dl.git $HOME/repos/youtube-dl

# zsh-completion
./git_install.sh git://github.com/zsh-users/zsh-completions.git $HOME/repos/zsh-completions
mkdir -p $HOME/._zshcomp

download_file_into() {
  local uri="$1"
  local path="$2"
  local filename=$(basename "$uri")
  curl -sL "$uri" | tee "${path}/${filename}" > /dev/null
}

download_file_into http://gemi.fedorapeople.org/haskell/_ghc   "$HOME/._zshcomp"
download_file_into http://gemi.fedorapeople.org/haskell/_hugs  "$HOME/._zshcomp"
download_file_into http://gemi.fedorapeople.org/haskell/_cabal "$HOME/._zshcomp"


# pacapt
PACAPT_DIR="$HOME/repos/pacapt"
./git_install.sh git://github.com/icy/pacapt.git $PACAPT_DIR

if [ -f "/etc/os-release" ]; then
  source /etc/os-release
  if [ 'arch' != $ID ]; then
    cd /usr/bin; sudo ln -sv "${PACAPT_DIR}/pacapt/pacman" .
  fi
fi


