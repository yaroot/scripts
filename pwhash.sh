#!/usr/bin/env bash

salt_file="/tmp/${USER}_salt"

which sha256sum &> /dev/null && SHA256SUM=`which sha256sum`
which shasum &> /dev/null && SHA256SUM="`which shasum` -a 256"

# generate pwfile
if [ "$1" == '-g' ]; then
  read -s -p 'seed: ' seed
  echo ''

  if [ -z "$seed" ]; then
    echo 'Error: no seed provided' 1>&2
    exit 1
  fi

  touch "$salt_file"
  chmod 600 "$salt_file"

  eval "echo \"$seed\" | $SHA256SUM | cut -d' ' -f1 | tee $salt_file > /dev/null"
  echo "salt generated to $salt_file"
  ls -alh "$salt_file"
  exit 0
fi

if [ ! -f "$salt_file" ]; then
  echo 'Error: no salt file' 1>&2
  exit 1
fi

if [ "$1" == '-m' ]; then
  \which dmenu &> /dev/null
  if [ ! "$?" == "0" ]; then
    echo "Error: -m need dmenu" 1>&2
    exit 1
  fi

  dmenurc=`cat $HOME/.dmenurc 2> /dev/null`
  site=$(xclip -o | dmenu -i $dmenurc -p `basename $0`)
  eval "$0 -c $site"
  exit
fi

copy='no'
if [ "$1" == '-c' ]; then
  shift
  if [ `uname -s` == 'Darwin' ]; then
    copy='| pbcopy'
  else
    # xorg
    copy='| xclip -selection clipboard'
  fi
fi


site="$1"
if [ "x$site" = "x" ]; then
  echo "Erro: please give something to hash" 1>&2
  exit 1
fi

pwhash=$(echo "${site}`cat $salt_file`" | $SHA256SUM)
pass=${pwhash:1:10}

if [ "$copy" == 'no' ]; then
  echo "$pass"
else
  eval "echo -n \"$pass\" $copy"
fi

