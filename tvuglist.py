#!/usr/bin/env python

import tvug

with open('list.txt') as f:
    for line in f.lines():
        tvug.get(line.strip())

