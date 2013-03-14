#!/usr/bin/env python2

from __future__ import print_function, unicode_literals, division
import requests
import argparse
import subprocess

def filter_None(x):
    if x is None:
        return False
    return True

def shell_out(cmd):
    try:
        r = subprocess.check_output(cmd.split(' '))
        s = r.strip()
        if len(s) > 2:
            return s
        else:
            return None
    except subprocess.CalledProcessError:
        pass
    return None

def get_account_info(acc):
    user = shell_out('git config %s.name' % acc)
    passwd = shell_out('git config %s.passwd' % acc)
    if user is None or passwd is None:
        return None
    else:
        return (user, passwd)

def main(args):
    accounts = args.target
    print(accounts)
    if accounts is None:
        accounts = ['github', 'bitbucket']
    accs = map(get_account_info, accounts)
    print(accs)
    # for account in args.account:
    #     for repo in args.create:
    #         print(account, repo)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--private', action='store_true', default=False, help="mark repo private [create only]")
    parser.add_argument('-t', '--target', nargs='+',  help="targets account, should be list in ~/.gitconfig")
    parser.add_argument('-c', '--create', nargs='+', help="repo names to be created")
    args = parser.parse_args()
    main(args)
