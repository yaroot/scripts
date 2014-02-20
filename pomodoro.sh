#!/usr/bin/env bash

function main()
{
  local limit="$1"
  test -z "$timer" && limit=25

  local date_format="+%R"
  local counter=0
  local starttime=`date $date_format -d 'now'`
  local endtime=`date $date_format -d "now + $limit min"`

  echo "[Pomodoro] started, stint will end at <$endtime>"
  notify-send --urgency low "[Pomodoro] started" "stint will end at $endtime"

  while [ $counter != $limit ]; do
    let "counter++"
    echo "[Pomodoro] `expr $limit - $counter + 1` min left"
    sleep 1m
  done

  echo "[Pomodoro] stint ended (started at <$starttime>)"
  notify-send --urgency critical  "[Pomodoro] ended" "started at $starttime"
}

main $*
