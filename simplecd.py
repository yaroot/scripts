#!/usr/bin/env python2

from __future__ import unicode_literals, division, print_function
import requests

def parseDownloadPage(line):
    ls = line.split('"')
    if len(ls) == 5 and ls[3].startswith('/download/?'):
        return ls[3]
    else:
        return None

def parsePage(url):
    links = list()
    r = requests.get(url)
    for l in r.text.splitlines():
        res = parseDownloadPage(l)
        if res is not None:
            links.append(res)
    return links

BASEURL='http://simplecd.me'
def parseDownloadURL(link):
    url = BASEURL + link
    r = requests.get(url)
    for l in r.text.splitlines():
        split = l.split('"')
        if len(split) == 7 and split[5].startswith('ed2k://'):
            print(split[5].encode('UTF-8'))

def main(url):
    proglist = parsePage(url)
    for link in proglist:
        print(parseDownloadURL(link))

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
