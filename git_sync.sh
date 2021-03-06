#!/usr/bin/env bash
# a helper script deal with git-svn dcommit/push/merge stuff
# git svn clone --prefix=svn/ svn://repo/url [-s]

set -e

SVN_PREFIX='svn'

run() {
  echo "[INFO] Running >>> $@"
  eval "$1"
}

main(){
  local branch=`git symbolic-ref HEAD`
  if [ -n "$1" ]; then
    branch="$1"
  else
    branch=${branch#refs/heads/}
  fi

  local has_stash=false
  if [ -n "`git status --porcelain`" ]; then
    has_stash=true
    run "git stash"
  fi

  local is_git_svn_repo=true
  if [ -z "`git config --get svn-remote.svn.url`" ]; then
    is_git_svn_repo=false
  fi

  for remote in `git remote`; do
    run "git fetch $remote"
    run "git rebase $remote/$branch"
    run "git merge $remote/$branch"
  done

  if $is_git_svn_repo; then
    # run "git rebase $branch"
    run "git svn fetch"
    # run "git svn rebase"
    run "git rebase $SVN_PREFIX/$branch"
    run "git svn dcommit"
  fi

  for remote in `git remote`; do
    cmd="git push $remote ${branch}:${branch}"
    if $is_git_svn_repo; then
      cmd="$cmd -f"
    fi
    run "$cmd"
  done

  if $has_stash; then
    run "git stash pop" # apply stash?
  fi
}

main $@

