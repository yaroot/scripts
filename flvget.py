#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, print_function, unicode_literals, division
import sys
import subprocess
try:
    import requests
except ImportError:
    print("[requests] package is required, run `pip install requests` to get it")
    sys.exit(1)

FirefoxUA = '''Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0'''
FNAME = '<input type="hidden" name="name" value="'
FLIST = '<input type="hidden" name="inf" value="'

def ParseDownloadLinks(page):
    found = False
    linkList = list()
    name = None
    c = 1

    for line in page.splitlines():
        if line.find(FNAME) > -1:
            name = line[len(FNAME): len(line)-2]

        if line.find(FLIST) > -1:
            found = True
        if found:
            if line.find('"/>') == 0:
                break
            if line.find(FLIST) > -1:
                pair = dict()
                pair['url'] = line[len(FLIST):]
                pair['name'] = name + str(c).decode('utf-8')
                linkList.append(pair)
                c = c+1
            else:
                pair = dict()
                pair['url'] = line
                pair['name'] = name + str(c).decode('utf-8')
                linkList.append(pair)
                c = c+1

    return linkList


def DownloadFlv(links):
    for pair in links:
        name = '%s.flv' % pair['name']
        url  = pair['url']

        try_curl = False
        try:
            subprocess.call(['wget', '--user-agent', FirefoxUA,
                '-O', name, url])
        except OSError:
            try_curl = True
        if try_curl:
            try:
                subprocess.call(['curl', '--user-agent', FirefoxUA,
                    '-L', '-o', name, url])
            except OSError:
                pass


def RequestDownloadLink(link):
    payload = { 'kw': link,
            'format': 'super' }
            # 'flag': 'one',

    r = requests.get('http://www.flvcd.com/parse.php', params=payload)
    webcontent = r.content.decode('GBK')
    links = ParseDownloadLinks(webcontent)
    if len(links) > 0:
        DownloadFlv(links)


def main():
    if len(sys.argv) < 1:
        raise Exception("Need at least one URL")
    RequestDownloadLink(sys.argv[1])


    pass

if __name__ == '__main__':
    main()

