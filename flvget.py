#!/usr/bin/env python

from __future__ import absolute_import, print_function, unicode_literals, division
import sys
import subprocess
try:
    import requests
except ImportError:
    print("[requests] package is required, run `pip install requests` to get it")
    sys.exit(1)

FirefoxUA = '''Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0'''

def ParseDownloadLinks(page):
    found = False
    linkList = list()
    pair = dict()

    for line in page.splitlines():
        if line.find('''<input type="hidden" name="name"''') > -1:
            found = True

        if found:
            if line.find('<strong>') == 0:
                break
            if line.find('<N>') > -1:
                pair['name'] = line.replace('<N>', '')
            elif line.find('<U>') > -1:
                pair['url'] = line.replace('<U>', '')
            
            if pair.has_key('name') and pair.has_key('url'):
                linkList.append(pair)
                pair = dict()
        
    return linkList


def DownloadFlv(links):
    for pair in links:
        name = '%s.flv' % pair['name']
        url  = pair['url']
        subprocess.call(['wget', '--user-agent', FirefoxUA,
            '-O', name, url])

def RequestDownloadLink(link):
    payload = { 'kw': link,
            'flag': 'one',
            'format': 'super' }

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

