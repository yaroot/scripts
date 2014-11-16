#!/usr/bin/env python2
# TODO
# - handle arguments to execlp new program
# - should be rewrite in c to be used in production?

import os, signal

def daemonize(umask=None, jail_dir=None, uid=None, gid=None):
    pid = os.fork()

    # fork failed
    if pid < 0:
        raise RuntimeError('os.fork() failed')

    # terminate parent
    if pid > 0:
        os._exit(0)

    os.setsid()

    # ignore signals
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    pid = os.fork()
    if pid < 0:
        raise RuntimeError('os.fork() failed')

    # terminate parent
    if pid > 0:
        os._exit(0)

    if umask:
        os.umask(umask)

    if jail_dir:
        os.chroot(jail_dir)
        os.chdir('/')

    if uid and gid and os.getuid == 0:
        os.setgroups([])
        os.setgid(gid)
        os.setuid(uid)


if __name__ == '__main__':
    daemonize()
