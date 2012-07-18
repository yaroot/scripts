#!/usr/bin/env bash

tmp_dir='/tmp/pkgfiles'
pfile_dir='/var/pkgfiles'

download_flist() {
  local repo="$1"
  local mirror="$2"
  local tarball="${repo}.files.tar.gz"
  local download_url="${mirror}/${tarball}"

  echo ">> Downloading $furl"

  cd $tmp_dir
  #wget -q "$furl"
  curl --progress-bar "$furl" -O

  mkdir "$repo"
  tar zxf "$tarball" -C "$repo"

  find "./${repo}" -name 'desc' -delete
  find "./${repo}" -name 'depends' -delete

  rsync -r --delete "${repo}" "${pfile_dir}/"

  rm -rf "${repo}" "${tarball}"
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
