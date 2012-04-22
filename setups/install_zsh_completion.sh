#!/usr/bin/env bash

./git_install.sh git://github.com/zsh-users/zsh-completions.git $HOME/repos/zsh-completions


if [ ! -d "$HOME/._zshcomp" ]
then
    mkdir $HOME/._zshcomp
fi

download()
{
    uri="$1"
    path="$2"
    filename=$(basename "$uri")
    curl -s "$uri" | tee "${path}/${filename}" > /dev/null
}

download http://gemi.fedorapeople.org/haskell/_ghc       $HOME/._zshcomp
download http://gemi.fedorapeople.org/haskell/_hugs      $HOME/._zshcomp
download http://gemi.fedorapeople.org/haskell/_cabal     $HOME/._zshcomp

