#!/usr/bin/env sh

REPO_URL="$1"
CLONE_PATH="$2"

if [ -d "$CLONE_PATH" ]; then
  cd $CLONE_PATH

  echo ">>>>> Updating [`pwd`]"
  git pull --ff-only
else
  echo ">>>>> Cloning [${REPO_URL}] into [${CLONE_PATH}]"
  git clone "$REPO_URL" $CLONE_PATH
fi

