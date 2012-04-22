#!/bin/bash

node="$1"


./remote.sh -t "$node" sudo yum update -y

