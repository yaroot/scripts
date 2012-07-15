#!/usr/bin/env bash

# youtube-dl
./git_install.sh git://github.com/rg3/youtube-dl.git $HOME/repos/youtube-dl

# zsh-completion
./git_install.sh git://github.com/zsh-users/zsh-completions.git $HOME/repos/zsh-completions
mkdir -p $HOME/._zshcomp

./git_install.sh git://github.com/yaroot/etc.git $HOME/repos/etc

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
# sudo ln -sv "${PACAPT_DIR}/pacapt/pacman" /usr/bin/pacman

