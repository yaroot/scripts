#!/usr/bin/env bash

# http://mirrors.163.com/archlinux/core/os/x86_64/core.files.tar.gz

tmp_dir='/tmp/pkgfiles'
pfile_dir='/var/pkgfiles'

download_flist() {
  local pname="$1"
  local mirror="$2"
  local furl="${mirror}/${pname}.files.tar.gz"

  echo ">> Downloading $furl"

  cd $tmp_dir
  wget -q "$furl"

  local fname

  pname="${repo}.files"
  fname=`basename $furl`

  mkdir "$pname"
  tar zxf "$fname" -C "$pname"

  find "./${pname}" -name 'desc' -delete
  find "./${pname}" -name 'depends' -delete

  rsync -r --delete "${pname}" $pfile_dir

  rm -rf "${pname}" "${fname}"
}

update_filelist() {
  mkdir -p $tmp_dir
  rm -rf "$tmp_dir/*"

  rm -rf "$pfile_dir/*"
  mkdir -p $pfile_dir

  local script_dir
  script_dir=`dirname ${BASH_SOURCE}`
  for line in `lua $script_dir/pacman_parse_repos.lua`; do
    download_flist `echo $line | tr '#' ' '`
  done

  rm -rf $tmp_dir
  echo ">> Done updating"
}

main() {
  local i="$1"
  if [ -z "$i" ]; then
    echo "Usage: $0 -u/[file name]"
    exit 1
  fi

  if [ '-u' = "$1" ]; then
    update_filelist
    shift
  fi

  i="$1"
  if [ -z "$i" ]; then
    exit 0
  fi

  cd "$pfile_dir"
  ack -a "$1"

  exit $?
}

main $@
