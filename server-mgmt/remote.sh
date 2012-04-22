#!/bin/bash

exec ssh -x -o "BatchMode yes" "$@"

