#!/usr/bin/env python

from __future__ import absolute_import, print_function, unicode_literals, division

import request




def parse_cfg_line(line):


def read_cfg_by_line(fd):
    alist = list()
    for line in fd.lines():
        a = parse_cfg_line(line)
        if a:
            alist.append(a)
    return alist


def parse_config(cfg_file):
    try:
        with open(cfg_file) as f:
            cfg = read_cfg_by_line(f)
            return cfg
    except IOError:
        raise Exception("Open [{}] error".format(cfg_file))


def main(argv):
    addon_list = parse_config('addon.cfg')

if __name__ == '__main__':
    import sys
    main(sys.argv)
