#!/usr/bin/env bash

ZSHCOMP="$HOME/.local/zshcomp"

symlink() {
  local src="$1"
  local tar="$2"

  mkdir -p `dirname "$tar"`
  rm -f "$tar"
  ln -sv "$src" "$tar"
}

./git_install.sh git://github.com/visionmedia/n.git $HOME/.local/n

./git_install.sh git://github.com/sstephenson/rbenv.git $HOME/.rbenv
./git_install.sh git://github.com/sstephenson/ruby-build.git $HOME/.rbenv/plugins/ruby-build
./git_install.sh git://github.com/jamis/rbenv-gemset.git $HOME/.rbenv/plugins/rbenv-gemset

./git_install.sh git://github.com/technomancy/leiningen.git $HOME/repos/leiningen
symlink $HOME/repos/leiningen/zsh_completion.zsh $HOME/.local/zshcomp/_lein

# ./git_install.sh git://github.com/pypa/virtualenv.git $HOME/repos/virtualenv

./git_install.sh git://github.com/rg3/youtube-dl.git $HOME/repos/youtube-dl

./git_install.sh git://github.com/defunkt/hub.git $HOME/repos/hub
pushd $HOME/repos/hub; rake standalone; cp hub $HOME/.local/bin/;
cp etc/hub.zsh_completion ${ZSHCOMP}/_hub; popd;

./git_install.sh git://github.com/zsh-users/zsh-completions.git $HOME/.local/zsh-completions

download_file_into() {
  local uri="$1"
  local path="$2"
  local filename=$(basename "$uri")
  mkdir -p $path
  curl -sL "$uri" | tee "${path}/${filename}" > /dev/null
}

download_file_into http://gemi.fedorapeople.org/haskell/_ghc   $ZSHCOMP
download_file_into http://gemi.fedorapeople.org/haskell/_hugs  $ZSHCOMP
download_file_into http://gemi.fedorapeople.org/haskell/_cabal $ZSHCOMP

./git_install.sh git://github.com/icy/pacapt.git "$HOME/repos/pacapt"

