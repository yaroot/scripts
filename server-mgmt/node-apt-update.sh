#!/bin/bash

node="$1"

APT_ARGS="--assume-yes"

./remote.sh -t $node sudo apt-get update '&&' sudo apt-get upgrade ${APT_ARGS} '&&' sudo apt-get autoclean ${APT_ARGS}
# sudo apt-get dist-upgrade ${APT_ARGS}

