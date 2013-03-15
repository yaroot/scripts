#!/usr/bin/env python2

from __future__ import print_function, unicode_literals, division
import requests
import argparse
import subprocess

class Account(object):
    def __init__(self, name, passwd, typ):
        self.name = name
        self.passwd = passwd
        self.type = typ
    pass

def list_repo(account):
    print(account.type, account.name, account.passwd)

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
    _type = shell_out('git config %s.type' % acc)
    if _type is None:
        _type = acc
    if user is None or passwd is None:
        return None
    else:
        return Account(user, passwd, _type)

def main(args):
    taccs = args.target
    if taccs is None:
        taccs = ['github', 'bitbucket']
    accs = map(get_account_info, taccs)
    accs = filter(filter_None, accs)
    if args.list:
        for acc in accs:
            list_repo(acc)
    else if args.create:

    print(accs)
    # for account in args.account:
    #     for repo in args.create:
    #         print(account, repo)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--private', action='store_true', default=False, help="mark repo private [creation only]")
    parser.add_argument('-t', '--target', nargs='+',  help="targets account, should be list in ~/.gitconfig")
    parser.add_argument('-c', '--create', nargs='+', help="repo names to be created")
    parser.add_argument('-l', '--list', action='store_true', default=False, help="list repos")
    args = parser.parse_args()
    main(args)
