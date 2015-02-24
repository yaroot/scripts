#!/usr/bin/env bash

test ! -f $HOME/.repo_mirrors.conf && exit 1

set -e

rm -rf $HOME/.mirror_sync_tmp
mkdir $HOME/.mirror_sync_tmp

alert() {
  echo ">>> $@"
}

for repo in `cat $HOME/.repo_mirrors.conf`; do
  test -z "${repo}" && continue
  test "${repo:0:1}" = "#" && continue

  REPO="$repo"
  PRIVATE=0
  if [ "${repo:0:1}" = "!" ]; then
    REPO=${repo:1}
    PRIVATE=1
  fi
  test $PRIVATE = 1 && continue

  alert "Syncing $REPO"
  cd $HOME/.mirror_sync_tmp
  git clone --mirror git://github.com/yaroot/${REPO}.git
  cd ${REPO}.git

  git remote add bb git@bitbucket.org:yaroot/${REPO}.git
  git remote add gc git@gitcafe.com:yaroot/${REPO}.git
  alert "Pushing bitbucket"
  git push --mirror bb
  alert "Pushing gitcafe"
  git push --mirror gc
done

