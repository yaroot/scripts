#!/usr/bin/env python

from __future__ import absolute_import, print_function, unicode_literals

import sys
import datetime as DT


def format_dt(ts):
    time = DT.datetime.fromtimestamp(ts)
    return time.strftime('%Y-%m-%d %H:%M:%S')

def format_datatransfer(n):
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


def format_disconnect(line):
    contype, name, ip, port, sent, recv, unixts, timestr = tuple(line.split(','))
    size = format_datatransfer(int(sent)+int(recv))
    dt = format_dt(int(unixts))
    return "%(name)s\t\t%(size)s\t%(date)s" % \
            {'name': name, 'date': dt, 'size': size}


def format_line(line):
    if line.startswith('client-disconnect'):
        return format_disconnect(line)
    elif line.startswith('client-connect'):
        return None



def print_log_fd(fd):
    for line in fd.readlines():
        if len(line.strip()) > 5:
            formatted = format_line(line.strip())
            if formatted is not None:
                print(formatted)


def main():
    logfile = '/etc/openvpn/client_update.log'
    if len(sys.argv) > 1:
        logfile = sys.argv[1]
    with open(logfile, 'r') as f:
        print_log_fd(f)


if __name__ == '__main__':
    main()

