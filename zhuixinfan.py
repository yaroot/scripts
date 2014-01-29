#!/usr/bin/env python2
# encoding=utf-8

from __future__ import unicode_literals
import re
import requests
import base64


def parse_obscured_links(line):
    """
        种子</a><a href=""
    """
    if line.find('种子') > 0:
        match = re.search('''种子</a><a href="(.+?)"''', line)
        if match:
            grps = match.groups()
            if len(grps) == 1:
                return grps[0]
    return None


def parse_base64_str_from_url(url):
    _ENCRYPT = 'encypt='
    i = url.find(_ENCRYPT)
    b64 = url[i + len(_ENCRYPT):]
    return b64.replace('%3D%3D', '==')


def decode_b64_ed2k(b64):
    almost_ed2k = base64.b64decode(b64).decode('ascii')
    i = almost_ed2k.find('ed2k://')
    return almost_ed2k[i:]


def main(url):
    r = requests.get(url)
    if not r.ok:
        print '[ERROR] fetching page error: %d' % r.status_code
        import os
        os.exit(-1)

    obs_urls = filter(lambda x: x is not None, [ parse_obscured_links(line) for line in r.text.splitlines() ])
    base64grp = [ parse_base64_str_from_url(url) for url in obs_urls ]
    ed2ks = [ decode_b64_ed2k(b) for b in base64grp ]
    for e in ed2ks:
        print e


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
