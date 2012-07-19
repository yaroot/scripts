#!/usr/bin/env bash

gen_list() {
  local base="$1"
  local code="$2"
  local comp='main contrib non-free'


  echo ''
  echo ''

  echo "deb http://$base/debian $base $comp"
  echo "deb-src http://$base/debian $base $comp"
  echo ''

  echo "deb http://$base/debian ${base}-updates $comp"
  echo "deb-src http://$base/debian ${base}-updates $comp"
  echo ''

  echo "deb http://$base/debian-security $base/updates $comp"
  echo "deb-src http://$base/debian-security $base/updates $comp"
  echo ''

  echo "deb http://$base/debian-backports ${base}-backports $comp"
  echo ''

  echo "deb http://security.debian.org/ ${base}/updates $comp"
  echo "deb-src http://security.debian.org/ ${base}/updates $comp"
  echo ''

  echo "deb http://backports.debian.org/debian-backports ${base}-backports $comp"
  echo ''
}

case $1 in
  jaist) gen_list 'http://ftp.jaist.ac.jp/pub/Linux' 'squeeze' ;;
  osuosl) gen_list 'http://mirrors.osuosl.org' 'squeeze' ;;
  kernel) gen_list 'http://mirrors.us.kernel.org' 'squeeze' ;;
  nchc) gen_list 'http://ftp.nchc.org.tw' 'squeeze' ;;
  163) gen_list 'http://mirrors.163.com' 'squeeze' ;;
esac

