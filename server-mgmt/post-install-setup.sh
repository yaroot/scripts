#!/bin/sh
# curl -L https://github.com/yaroot/scripts/raw/master/server-mgmt/post-install-setup.sh | sh

PACKAGES="base-devel sudo iptables start-stop-daemon \
  openssh dante sshguard ntp curl wget netcfg  python2 lesspipe \
  vim tmux git zsh atool unzip unrar iotop htop bwm-ng ack "

DIST=''
if [ -f /etc/arch-release ]; then
  DIST='arch'
elif [ -f /etc/debian_version ]; then
  DIST='debian'
fi

run() {
  echo "-> $@"
  eval "$@"
}

save_file_to() {
  local url="$1"
  local to="$2"

  run "curl -qL '$url' | tee '$to' > /dev/null"
}

install_packages() {
  if [ 'debian' = "$DIST" ]; then
    run apt-get install -y $PACKAGES
  elif [ 'arch' = "$DIST" ]; then
    run pacman -Syy
    run pacman -S --noconfirm archlinux-keyring
    run pacman -Su --needed --noconfirm $PACKAGES
  fi
}

post_install_arch() {
  save_file_to 'https://github.com/yaroot/dotfiles/raw/master/etc/arch/rc-local.service' /usr/lib/systemd/system/rc-local.service
  save_file_to 'https://github.com/yaroot/dotfiles/raw/master/etc/arch/rc.local' /etc/rc.local
  run chmod +x /etc/rc.local

  run systemctl enable multi-user.target

  run systemctl enable rc-local.service

  run systemctl enable cronie.service
  run systemctl enable sshd.service
  run systemctl enable sshguard.service

  run systemctl disable ip6tables.service
  run systemctl disable iptables.service

  run systemctl mask ip6tables.service
  run systemctl mask iptables.service
}

post_install_debian() {
  echo 1 > /dev/null
}

post_install() {
  if [ 'arch' = "$DIST" ]; then
    post_install_arch
  elif [ 'debian' = "$DIST" ]; then
    post_install_debian
  fi

  local TERMR='/usr/share/terminfo/r'
  run mkdir -p $TERMR
  save_file_to 'https://github.com/yaroot/dotfiles/raw/master/etc/rxvt/rxvt-unicode-256color' $TERMR/rxvt-unicode-256color
  save_file_to 'https://github.com/yaroot/dotfiles/raw/master/etc/rxvt/rxvt-unicode' $TERMR/rxvt-unicode
}

add_user() {
  local USER='yaroot'
  local GROUP='users'
  run useradd -m -g $GROUP -G wheel -s /bin/bash $USER

  local sshdir="/home/$USER/.ssh"
  local authfile="$sshdir/authorized_keys"

  run mkdir -p $sshdir
  run touch $authfile
  run chmod 600 $authfile

  run "echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDQ4v/HyXZaIXopbipOIrBnPi9VR3xmbslAjusxi9cYbUiiusHYMXNDLoc6oK6QuRVIqLUcsm4YtAgTQm5rNJIHsTfzyJlmUxbU0reKZ93UOK2/IlliwvXZjreZm/9LqeNunCpuomv9UZl7tMV5HSVyxD4+/aaycPCQzT14UdXrSYNScfCyGLOHrwNfrSZ9Y9rXqxN9bPhVDWj+ItcIIhZSwysHhUvYZo/5Cdz/eBF3ICAhgHv8OzbXkClyuScxhRdRB37RrnMN08Iu39XJEO8RdpgRavMAai/Wj+qhkw9oPbfVcfW8EtglaQ/0aUaEBgcktocpWFg4KxZ9rgd2aJuj yaroot@default' >> $authfile"

  run chown -R $USER:$GROUP $sshdir
}

helpmsg() {
  echo '**************************'
  echo '> All Done'
  echo '> now change user passwd and clone your dotfile'
  echo '> git clone git://github.com/yaroot/scripts.git $HOME/.bin'
}

main() {
  install_packages
  post_install
  add_user

  helpmsg
}

main

