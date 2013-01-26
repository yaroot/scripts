#!/bin/bash

restart_racoon() {
  RACOON_PROF='com.apple.racoon'
  launchctl stop $RACOON_PROF
  launchctl start $RACOON_PROF

  echo "*** done fix racoon, please reconnect vpn ***"
}

restore_racoon() {
  sed -i.bak 's/^# include/include/' /etc/racoon/racoon.conf
  sed -i.bak '/^include\ "\/etc\/racoon\/remotes.*/d' /etc/racoon/racoon.conf

  restart_racoon
}


main() {
  local prof="$1"
  if [ -z "$prof" ]; then
    restore_racoon
    exit 0;
  fi

  local origconfdir="/var/run/racoon"
  local remotes="/etc/racoon/remotes"

  mkdir -p $remotes
  rm -f "$remotes/$prof"

  sed 's/3600 sec/24 hour/' "$origconfdir/$prof" > "$remotes/$prof"

  # configure racoon and restart

  sed -i 's/^include\ "\/var/# include "\/var/' /etc/racoon/racoon.conf
  echo 'include "/etc/racoon/remotes/*.conf" ;' >> /etc/racoon/racoon.conf

  restart_racoon
}

main $@

