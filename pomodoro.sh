#!/usr/bin/env bash

function main()
{
  local limit="$1"
  test -z "$limit" && limit=25

  local date_format="+%R"
  local counter=0
  local starttime=`date $date_format -d 'now'`
  local endtime=`date $date_format -d "now + $limit min"`

  echo "[Pomodoro] <$endtime> push push push"
  notify-send --urgency low "Pomodoro [$endtime]" "push push push"

  local left

  while [ $counter != $limit ]; do
    let "counter++"
    left=`expr $limit - $counter + 1`
    echo "[Pomodoro] L${left}"
    sleep 1m
  done

  echo "[Pomodoro] <$starttime> box box box"
  notify-send --urgency critical  "Pomodoro [$starttime]" "box box box"
}

main $*
