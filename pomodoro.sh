#!/usr/bin/env bash

function main()
{
  local limit="$1"
  test -z "$limit" && limit=25

  local date_format="+%R"
  local counter=0
  local starttime=`date $date_format -d 'now'`
  local endtime=`date $date_format -d "now + $limit min"`

  echo "[Pomodoro] stint start, push push push until <$endtime>"
  notify-send --urgency low "Pomodoro [$endtime]" "push push push"

  local left

  while [ $counter != $limit ]; do
    let "counter++"
    left=`expr $limit - $counter + 1`
    echo "[Pomodoro] ${left} min to go"
    # sleep 1m
  done

  echo "[Pomodoro] stint ended (started at <$starttime>)"
  notify-send --urgency critical  "Pomodoro [$starttime]" "box box box"
}

main $*
