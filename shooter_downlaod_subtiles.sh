#!/usr/bin/env bash
#
# This script use `sscl` command line tool inside SPlayer for mac
# to download the subtitles
#

which sscl &> /dev/null
if [ ! $? -eq 0 ]; then
    echo "Can't find sscl"
    echo "please download from here: 'http://hg.splayer.org/splayerx/raw/0b9e84441210/binaries/x86_64/sscl'"
    echo "and put it in your PATH"
    exit 1
fi


if [ $# -eq 0 ]; then
    echo "ERROR: please choose movies to download subtitle"
    exit 1
fi


for movie_file in "$@"; do
    echo "Downloading subtitle for > $movie_file <"
    movie_path=`dirname $movie_file`

    subtitles=$(sscl --video-file "$movie_file" --pull)

    while read sub_file; do
        mv "$sub_file" "$movie_path"
    done <<< "$subtitles"
done

