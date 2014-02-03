#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function, unicode_literals, division
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

def parse_flvcd_page(page):
    linkList = None
    name = None

    for line in page.splitlines():
        if line.find(FNAME) > -1:
            name = line[len(FNAME): -2]

        if line.find(FLIST) > -1:
            l = line[len(FLIST): -4]
            linkList = l.split('|')

    if name is not None and linkList is not None:
        return (name, linkList)
    else:
        return None


def download(url, fname):
    try_curl = False

    try:
        subprocess.call(['wget', '--user-agent', FirefoxUA,
            '-O', fname, url])
    except OSError:
        try_curl = True
    if try_curl:
        try:
            subprocess.call(['curl', '--user-agent', FirefoxUA,
                '-L', '-o', fname, url])
        except OSError:
            pass


def main():
    if len(sys.argv) < 1:
        raise Exception("Need at least one URL")
    payload = { 'kw': sys.argv[1],
            'format': 'super' }
            # 'flag': 'one',

    r = requests.get('http://www.flvcd.com/parse.php', params=payload)
    if not r.ok:
        sys.stderr.write("[ERROR] unable to fetch download url from flvcd.com")
        sys.exit(1)

    result = parse_flvcd_page(r.content.decode('GBK'))
    if result is not None:
        name, links = result
        for i, url in enumerate(links, start=1):
            file_name = '%s.%d.flv' % (name, i)
            download(url, file_name)


    pass

if __name__ == '__main__':
    main()

