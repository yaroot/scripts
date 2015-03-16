#!/usr/bin/env bash

GIT_PERSONAL_TOKEN=''

GIT_WORK_NAME=''
GIT_WORK_EMAIL=''

source $HOME/._git_user_conf

git filter-branch --env-filter '


if [ -n ` echo "$GIT_AUTHOR_EMAIL" | grep "$GIT_PERSONAL_TOKEN" `  ]; then
    export GIT_AUTHOR_NAME="$GIT_WORK_NAME"
    export GIT_AUTHOR_EMAIL="$GIT_WORK_EMAIL"
fi

if [ -n ` echo "$GIT_COMMITTER_EMAIL" | grep "$GIT_PERSONAL_TOKEN" `  ]; then
    export GIT_COMMITTER_NAME="$GIT_WORK_NAME"
    export GIT_COMMITTER_EMAIL="$GIT_WORK_EMAIL"
fi

'

