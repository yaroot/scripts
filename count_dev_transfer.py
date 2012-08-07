#!/usr/bin/env python

from __future__ import absolute_import, print_function, unicode_literals, division

import sys

def cat_file(path):
    with open(path, 'r') as f:
        return f.read()

def format_size(n):
    n = n / 1024
    if n < 1024:
        return '%d KB' % n
    n = n / 1024
    if n < 1024:
        return '%d MB' % n
    n = n / 1024
    if n < 1024:
        return '%d GB' % n
    n = n / 1024
    if n < 1024:
        return '%d TB' % n
    n = n / 1024
    return '%d PB' % n


def count_dev(dev):
    kls = '/sys/class/net/{0}/statistics/'.format(dev)
    rx = int(cat_file(kls + 'rx_bytes'))
    tx = int(cat_file(kls + 'tx_bytes'))
    print(dev, ' => [in] ', format_size(rx), '[out] ', format_size(tx))


def main(argv):
    if len(argv) > 1:
        for dev in argv[1:]:
            count_dev(dev)
    else:
        print("gimme dev(s)")

if __name__ == '__main__':
    import sys
    main(sys.argv)
