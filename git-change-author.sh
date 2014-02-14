#!/usr/bin/env bash

GIT_PERSONAL_TOKEN=''

GIT_WORK_NAME=''
GIT_WORK_EMAIL=''

source $HOME/._git_user_conf

#git filter-branch --env-filter '

an="$GIT_AUTHOR_NAME"
am="$GIT_AUTHOR_EMAIL"
cn="$GIT_COMMITTER_NAME"
cm="$GIT_COMMITTER_EMAIL"

if [ ` echo "$GIT_AUTHOR_EMAIL" | grep "$GIT_PERSONAL_TOKEN" > /dev/null `  ]; then
    export GIT_AUTHOR_NAME="$GIT_WORK_NAME"
    export GIT_AUTHOR_EMAIL="$GIT_WORK_EMAIL"
fi

if [ ` echo "$GIT_COMMITTER_EMAIL" | grep "$GIT_PERSONAL_TOKEN" > /dev/null `  ]; then
    export GIT_COMMITTER_NAME="$GIT_WORK_NAME"
    export GIT_COMMITTER_EMAIL="$GIT_WORK_EMAIL"
fi



# if [ "$GIT_COMMITTER_EMAIL" = "yaroot@gmail.com" ]
# then
#     cn="Your New Committer Name"
#     cm="Your New Committer Email"
# fi
# if [ "$GIT_AUTHOR_EMAIL" = "yaroot@gmail.com" ]
# then
#     an="Your New Author Name"
#     am="Your New Author Email"
# fi



#export GIT_AUTHOR_NAME="su_yan"
#export GIT_AUTHOR_EMAIL="su_yan@corp.netease.com"
#export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
#export GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
'

