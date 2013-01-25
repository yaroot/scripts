#!/bin/bash


print_help() {
  echo " Usage: run \`$0 'vpn_ip.conf'\` while connected to vpn"
  echo '        `ls /var/run/racoon` to get `vpn_ip`'
  echo ' change racoon config (/etc/racoon/racoon.conf)'
  echo '   from `include "/var/run/racoon/*.conf"` to'
  echo '        `include "/etc/racoon/remotes/*.conf"`'
}

main() {
  local prof="$1"
  if [ -z "$prof" ]; then
    print_help;
    exit 0;
  fi

  local origconfdir="/var/run/racoon"
  local remotes="/etc/racoon/remotes"

  mkdir -p $remotes
  rm -f "$remotes/$prof"

  sed 's/3600 sec/24 hour/' "$origconfdir/$prof" > "$remotes/$prof"

  # restart racoon

  RACOON_PROF='com.apple.racoon'

  launchctl stop $RACOON_PROF
  launchctl start $RACOON_PROF
}

main $@

