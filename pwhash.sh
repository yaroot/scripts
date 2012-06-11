#!/usr/bin/env bash

salt_file="/tmp/${USER}_salt"

\which sha256sum &> /dev/null && SHA256SUM=`which sha256sum`
\which gsha256sum &> /dev/null && SHA256SUM=`which gsha256sum`

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

copy='no'
if [ "$1" == '-c' ]; then
  shift
  if [ `uname -s` == 'Darwin' ]; then
    copy=' | pbcopy'
  else
    # xorg
    copy=' | xclip -selection clipboard'
  fi
fi


site="$1"

pwhash=$(echo "${site}`cat $salt_file`" | $SHA256SUM)
pass=${pwhash:1:10}

if [ "$copy" == 'no' ]; then
  echo "$pass"
else
  eval "echo $pass $copy"
fi

