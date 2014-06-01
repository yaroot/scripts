#!/usr/bin/env python2

from __future__ import unicode_literals
import sys
try:
    import json as simplejson
except:
    import simplejson

MAGIC_BOMB = '\uFEFF'

def main():
    raw = sys.stdin.read()
    if raw[0] == MAGIC_BOMB:
        raw = raw[1:]

    j = simplejson.loads(raw)
    s = simplejson.dumps(j, indent=2, ensure_ascii=False)
    sys.stdout.write(s.encode('utf-8'))
    sys.stdout.flush()

if __name__ == '__main__':
    main()

