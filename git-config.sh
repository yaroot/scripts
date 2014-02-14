#!/bin/sh

GIT_WORK_NAME=''
GIT_WORK_EMAIL=''

source $HOME/._git_user_conf

git config --local user.name "$GIT_WORK_NAME"
git config --local user.email "$GIT_WORK_EMAIL"
