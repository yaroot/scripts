#!/usr/bin/env bash
# pushes current branch to all remotes

set -e

SVN_PREFIX='svn'

run() {
  echo "[INFO] Running >>> $@"
#  eval "$1"
}

main(){
  local branch=`git symbolic-ref HEAD`
  if [ -n "$1" ]; then
    branch="$1"
    shift
  else
    branch=${branch#refs/heads/}
  fi

  local has_stash=false
  if [ -n "`git status --porcelain`" ]; then
    has_stash=true
    run "git stash"
  fi

  for remote in `git remote`; do
    cmd="git push $remote ${branch}:${branch}"
    run "$cmd $@"
  done

  if $has_stash; then
    run "git stash pop" # apply stash?
  fi
}

main $@

