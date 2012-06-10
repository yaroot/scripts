#!/bin/bash

salt_file="/tmp/${USER}_salt"
if [ ! -f "$salt_file" ]; then
  echo 'Error: no salt file' 1>&2
  exit 1
fi


INP="$1"

\which sha256sum &> /dev/null && SHA256SUM=`which sha256sum`
\which gsha256sum &> /dev/null && SHA256SUM=`which gsha256sum`

HASH=$(echo "${INP}`cat /tmp/${USER}_salt`" | $SHA256SUM)

echo ${HASH:1:10} | cut -f 1 -d ' '

