#!/bin/bash


node="$1"

f_deb="/etc/debian_version"
f_centos="/etc/redhat-release"

./remote.sh "$node" [ -f "$f_deb" ] '&&' 'echo debian  `cat ' "$f_deb" '`'
./remote.sh "$node" [ -f "$f_centos" ] '&&' cat "$f_centos"
./remote.sh "$node" uname -a


