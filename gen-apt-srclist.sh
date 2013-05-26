#!/usr/bin/env bash

gen_list() {
  local base="$1"
  local rel="$2"
  local comp='main contrib non-free'


  echo ''
  echo ''

  echo "deb http://$base/debian $rel $comp"
  echo "deb-src http://$base/debian $rel $comp"
  echo ''

  echo "deb http://$base/debian ${rel}-updates $comp"
  echo "deb-src http://$base/debian ${rel}-updates $comp"
  echo ''

  echo "deb http://$base/debian-security $rel/updates $comp"
  echo "deb-src http://$base/debian-security $rel/updates $comp"
  echo ''

  echo "deb http://$base/debian-backports ${rel}-backports $comp"
  echo ''

  echo "deb http://security.debian.org/ ${rel}/updates $comp"
  echo "deb-src http://security.debian.org/ ${rel}/updates $comp"
  echo ''

  echo "deb http://backports.debian.org/debian-backports ${rel}-backports $comp"
  echo ''
}

CODE='wheezy'
if [ -n "$2" ]; then
  CODE="$2"
fi

case $1 in
  jaist) gen_list 'ftp.jaist.ac.jp/pub/Linux' "$CODE" ;;
  osuosl) gen_list 'mirrors.osuosl.org' "$CODE" ;;
  kernel) gen_list 'mirrors.us.kernel.org' "$CODE" ;;
  nchc) gen_list 'ftp.nchc.org.tw' "$CODE" ;;
  163) gen_list 'mirrors.163.com' "$CODE" ;;
  ftp) gen_list 'ftp.debian.org' "$CODE" ;;
esac

