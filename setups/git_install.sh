#!/usr/bin/env bash



REPO_URL="$1"
LOCAL_CLONE="$2"

if [ -d "$LOCAL_CLONE" ]
then
    pushd "$LOCAL_CLONE"
    git pull
    popd
else
    mkdir -p "$LOCAL_CLONE"
    pushd "$LOCAL_CLONE"
    git init
    git remote add origin "$REPO_URL"
    git fetch origin
    git reset --hard origin/master
    git branch --set-upstream master origin/master
    popd
fi


