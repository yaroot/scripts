#!/usr/bin/env python2

from __future__ import unicode_literals
import os
import sys
import gzip

COMP_LEVEL = 9

def compress_file(fpath):
    foutpath = fpath + '.gz'
    sys.stdout.write('writing %s\n' % foutpath)
    sys.stdout.flush()
    with open(fpath, 'rb') as fin, gzip.open(foutpath, 'wb', COMP_LEVEL) as fout:
        fout.writelines(fin)


def main():
    for line in sys.stdin.readlines():
        fpath = line.strip()
        if fpath.endswith('.gz'):
            continue
        if not os.path.isfile(fpath):
            continue

        compress_file(fpath)


if __name__ == '__main__':
    main()

