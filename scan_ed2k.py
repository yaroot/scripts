#!/usr/bin/env python


import re, urllib2, sys


def get(link):
    content = urllib2.urlopen(link).read()
    match = re.findall(r'"(ed2k://\|file\|[^\"]+)"', content, re.S)
    links = list()
    for link in match:
        if link in links:
            continue
        else:
            links.append(link)
            print link

if __name__ == '__main__':
    get(sys.argv[1])

