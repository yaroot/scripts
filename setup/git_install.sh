#!/usr/bin/env bash



REPO_URL="$1"
LOCAL_CLONE="$2"


if [ ! -d "$LOCAL_CLONE" ]; then
  mkdir -p "$LOCAL_CLONE"
fi
pushd "$LOCAL_CLONE" > /dev/null

#if [ `git rev-parse --git-dir > /dev/null 2>&1` ]; then
if [ -d '.git' ]; then
  echo ">>>>> Updating [`pwd`]"
  git pull --ff-only
else
  echo ">>>>> Cloning [${REPO_URL}] into [`pwd`]"
  git clone "$REPO_URL" .
fi

popd > /dev/null

