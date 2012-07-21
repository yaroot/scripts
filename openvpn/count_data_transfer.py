#!/usr/bin/env python

from __future__ import absolute_import, print_function, unicode_literals, division

import sys
import datetime as DT

def format_dt(ts):
    time = DT.datetime.fromtimestamp(ts)
    return time.strftime('%Y-%m-%d %H:%M:%S')

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


SEC_MIN = 60
SEC_HR = 60*60

def format_duration(sec):
    if sec < 60:
        return '%dsec' % (sec)
    elif sec < 60*60:
        return '%dmin' % (sec/60)
    else:
        return '%.1fhr' % (sec / SEC_HR)

def align(nc, text):
    n = nc - len(text)
    if n > 0:
        return text + (' ' * n)
    else:
        return text


def format_disconnect(line):
    contype, name, ip, port, sent, recv, duration, timeunix, timestr = tuple(line.split(','))
    size = format_size(int(sent)+int(recv))
    dt = format_dt(int(timeunix))
    dur = format_duration(int(duration))
    name = align(20, name)

    return "%(name)s %(size)s\tin %(duration)s [%(date)s]" % \
            {'name': name, 'date': dt, 'size': size, 'duration': dur}


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

