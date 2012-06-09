#!/usr/bin/env bash



REPO_URL="$1"
LOCAL_CLONE="$2"


if [ ! -d "$LOCAL_CLONE" ]; then
  mkdir -p "$LOCAL_CLONE"
fi
pushd "$LOCAL_CLONE" > /dev/null

#if [ `git rev-parse --git-dir > /dev/null 2>&1` ]; then
if [ -d '.git' ]; then
  git pull
else
  git clone "$REPO_URL" .

#  git init
#  git remote add origin "$REPO_URL"
#  git fetch origin
#  git reset --hard origin/master
#  git branch --set-upstream master origin/master
fi

popd > /dev/null

