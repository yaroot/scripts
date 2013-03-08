#!/usr/bin/env sh



main(){
  local cmd="$1"
  shift;

  for node in "$@"; do
    ./remote.sh $node $cmd
  done
}

main $@

