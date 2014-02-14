#!/usr/bin/env python2
# coding=utf-8


import re, urllib2, sys

def get(link):
    content = urllib2.urlopen(link).read()
    match = re.findall(r'"(ed2k://\|file\|[^"]+)"', content, re.S)
    appeared = set()
    for link in match:
        if not link in appeared:
            appeared.add(link)
            print link

if __name__ == '__main__':
    get(sys.argv[1])

