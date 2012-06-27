#!/usr/bin/env bash

symlink() {
  local src="$1"
  local tar="$2"

  mkdir -p `dirname "$tar"`
  rm -f "$tar"
  ln -sv "$src" "$tar"
}

# n
./git_install.sh git://github.com/visionmedia/n.git $HOME/repos/n
mkdir -p $HOME/.nodes/{bin,lib,include}

# rbenv
./git_install.sh git://github.com/sstephenson/rbenv.git $HOME/.rbenv
./git_install.sh git://github.com/sstephenson/ruby-build.git $HOME/.rbenv/plugins/ruby-build
./git_install.sh git://github.com/jamis/rbenv-gemset.git $HOME/.rbenv/plugins/rbenv-gemset

# leiningen
./git_install.sh git://github.com/technomancy/leiningen.git $HOME/repos/leiningen
symlink $HOME/repos/leiningen/zsh_completion.zsh $HOME/._zshcomp/_lein

# virtualenv
./git_install.sh git://github.com/pypa/virtualenv.git $HOME/repos/virtualenv
