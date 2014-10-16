#!/usr/bin/env python2

from __future__ import unicode_literals
import re
import requests


def parse_xunlei_kuaichuan(u):
    page = requests.get(u).content.decode('utf-8')
    lines = [
        line
        for line in page.splitlines()
        if line.find('file_url') > -1
        if line.find('file_name') > -1
        if line.find('sendfile') > -1
    ]

    ret = set()
    for l in lines:
        m = re.search('file_url="(.*?)"', l)
        if m:
            ret.add(m.group(1))
    return ret


if __name__ == '__main__':
    import sys
    for u in sys.argv[1:]:
        try:
            for x in parse_xunlei_kuaichuan(u):
                print x.encode('utf-8')
        except Exception, e:
            import traceback
            traceback.print_exc()

