#!/usr/bin/env bash
# a helper script deal with git-svn dcommit/push/merge stuff
# git svn clone --prefix=svn/ svn://repo/url [-s]

set -e

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
    for remote in `git remote`; do
      run "git fetch $remote"
      run "git rebase $remote/$branch"
    done

    for remote in `git remote`; do
      run "git merge $remote/$branch"
      run "git push $remote"
    done
  else
    # git-svn repo

    for remote in `git remote`; do
      run "git fetch $remote"
      run "git rebase $remote/$branch"
      run "git merge $remote/$branch"
    done

    # run "git rebase $branch"
    run "git svn rebase"
    run "git svn dcommit"

    for remote in `git remote`; do
      run "git push $remote -f"
    done
  fi

  if $has_stash; then
    run "git stash apply"
  fi
}

main $@

