#!/usr/bin/env bash

BASEURL='http://commondatastorage.googleapis.com/chromium-browser-snapshots'

get_latest_for(){
  local os="$1"
  local target="$2"

  local latest=`curl -s $BASEURL/$os/LAST_CHANGE`
  if [ -z $latest ]; then
    echo '>>> Error reading version number' 1>&2
  fi

  curl --location --progress-bar "$BASEURL/$os/$latest/chrome-${target}.zip" -o "chrome-${target}-${latest}.zip"
}

get_latest_for 'Mac' 'mac'
get_latest_for 'Win' 'win32'


