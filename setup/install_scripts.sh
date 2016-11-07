#!/usr/bin/env sh

ZSHCOMP="$HOME/.local/zshcomp"

symlink() {
  local src="$1"
  local tar="$2"

  mkdir -p `dirname "$tar"`
  rm -f "$tar"
  ln -sv "$src" "$tar"
}

# ./git_install.sh git://github.com/visionmedia/n.git $HOME/.local/n
# ./git_install.sh git://github.com/ekalinin/nodeenv.git $HOME/repos/nodeenv

./git_install.sh git://github.com/sstephenson/rbenv.git $HOME/.rbenv
./git_install.sh git://github.com/sstephenson/ruby-build.git $HOME/.rbenv/plugins/ruby-build
# ./git_install.sh git://github.com/jamis/rbenv-gemset.git $HOME/.rbenv/plugins/rbenv-gemset
symlink $HOME/.rbenv/completions/rbenv.zsh $HOME/.local/zshcomp/_rbenv

# ./git_install.sh git://github.com/technomancy/leiningen.git $HOME/repos/leiningen
# symlink $HOME/repos/leiningen/zsh_completion.zsh $HOME/.local/zshcomp/_lein

# ./git_install.sh git://github.com/pypa/virtualenv.git $HOME/repos/virtualenv

./git_install.sh git://github.com/syl20bnr/spacemacs.git $HOME/.emacs.d

./git_install.sh git://github.com/zsh-users/zsh-completions.git $HOME/.local/zsh-completions

download_file_into() {
  local uri="$1"
  local filename="$2"
  local path="$3"
  mkdir -p $path
  curl -sL "$uri" | tee "${path}/${filename}" > /dev/null
}

# download_file_into http://gemi.fedorapeople.org/haskell/_ghc   _ghc $ZSHCOMP
# download_file_into http://gemi.fedorapeople.org/haskell/_hugs  _hugs $ZSHCOMP
# download_file_into http://gemi.fedorapeople.org/haskell/_cabal _cabal $ZSHCOMP

# ./git_install.sh git://github.com/defunkt/hub.git $HOME/repos/hub
# download_file_into http://defunkt.io/hub/standalone hub "$HOME/.local/bin"
# download_file_into https://github.com/defunkt/hub/raw/master/etc/hub.zsh_completion _hub $ZSHCOMP
# chmod +x $HOME/.local/bin/hub


./git_install.sh git://github.com/icy/pacapt.git "$HOME/repos/pacapt"

