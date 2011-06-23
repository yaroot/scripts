#!/usr/bin/env python

import tvug

with open('list.txt') as f:
    for line in f.readlines():
        tvug.get(line.strip())

