#!/usr/bin/env sh



main(){
  local cmd="$1"
  shift;

  for node in "$@"; do
    $cmd $node
  done
}

main $@

