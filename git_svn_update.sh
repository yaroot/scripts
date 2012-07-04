#!/usr/bin/env bash
# a helper script deal with git-svn dcommit/push/merge stuff

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
  local remote_branch="$SVN_PREFIX/$branch"
  echo "Branch: $branch"
  echo "Remote branch: $remote_branch"

  if [ "x`git config --get svn-remote.svn.url`" = "x" ]; then
    # git repo
    run "git fetch $REMOTE_NAME"
    run "git rebase $remote_branch"

    run "git merge $remote_branch"
    run "git push $REMOTE_NAME"
  else
    # git-svn repo
    run "git fetch $REMOTE_NAME"
    run "git rebase $REMOTE_NAME/$branch"
    run "git merge $REMOTE_NAME/$branch"

    # run "git rebase $branch"
    run "git svn rebase"
    run "git svn dcommit"

    run "git push $REMOTE_NAME --all -f"
  fi
}

main $@

