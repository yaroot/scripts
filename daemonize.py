#!/usr/bin/env python2

import os, signal

def daemonize(args):
    if os.fork() == 0:
        os.setsid()
        signal.signal(signal.SIGHUP, signal.SIG_IGN)

        if os.fork() == 0:
            prog = args.pop()
            argv = tuple(args)
            # os.execl(prog, argv)
            os.execlp(prog, argv)
        else:
            os._exit(0)
    else:
        os._exit(0)

if __name__ == '__main__':


