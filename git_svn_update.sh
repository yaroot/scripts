#!/usr/bin/env bash
# a helper script deal with git-svn dcommit/push/merge stuff
# git svn clone --prefix=svn/ svn://repo/url [-s]

set -e

REMOTE_NAME='origin'
SVN_PREFIX='svn'

run() {
  echo ">>> Running [$1]"
  eval "$1"
}

main(){
  local branch=`git symbolic-ref HEAD`
  branch=`basename $branch`
  if [ ! -z "$1" ]; then
    branch="$1"
  fi

  local has_stash=false
  if [ ! "x`git status --porcelain`" = "x" ]; then
    has_stash=true
    run "git stash"
  fi

  if [ "x`git config --get svn-remote.svn.url`" = "x" ]; then
    # git repo
    run "git fetch $REMOTE_NAME"
    run "git rebase $REMOTE_NAME/$branch"

    run "git merge $REMOTE_NAME/$branch"
    run "git push $REMOTE_NAME"
  else
    # git-svn repo
    run "git fetch $REMOTE_NAME"
    run "git rebase $REMOTE_NAME/$branch"
    run "git merge $REMOTE_NAME/$branch"

    # run "git rebase $branch"
    run "git svn rebase"
    run "git svn dcommit"

    run "git push $REMOTE_NAME -f"
  fi

  if $has_stash; then
    run "git stash apply"
  fi
}

main $@

