#!/usr/bin/env python2
# coding=utf-8

import os
import sys
import glob


def error_java_home_not_set():
    sys.stderr.write('Cannot find JAVA in system, `JAVA_HOME` not set\n')


def get_current_version():
    return os.environ.get('JAVA_HOME')


def clean_up_path(path, cur_jvm_home):
    return [
        p
        for p in path
        if not p.startswith(cur_jvm_home)
    ]

def find_jvm_home_by_token(token):
    if os.path.isdir(token):
        return token

    # try find it in /opt
    p = os.path.join('/opt', token)
    if os.path.isdir(p):
        return p

    # try glob match token in opt
    matches = glob.glob(os.path.join('/opt', token + '*'))
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        sys.stderr.write('Find multiple matches, please be more specific:\n')
        for m in matches:
            sys.stderr.write('    - %s\n' % m)


def print_current_version():
    java_home = get_current_version()
    if java_home is None:
        error_java_home_not_set()
        return
    sys.stderr.write('Found JAVA_HOME => [`%s`]\n' % java_home)


def print_switch_info(new_java_home, new_path):
    np = ':'.join(new_path)
    sys.stderr.write('Swtiching JAVA_HOME => [%s]\n' % new_java_home)
    sys.stderr.write('Swtiching PATH => [%s]\n' % np)


def print_switch_eval(new_java_home, new_path):
    np = ':'.join(new_path)
    sys.stdout.write('''##### EVAL START ####\n''')
    sys.stdout.write('''export PATH='%s';\n''' % np)
    sys.stdout.write('''export JAVA_HOME='%s';\n''' % new_java_home)
    sys.stdout.write('''##### EVAL END ####\n''')


def switch_java_version(new_ver):
    java_home = get_current_version()
    if java_home is None:
        error_java_home_not_set()
        return
    new_java_home = find_jvm_home_by_token(new_ver)
    if new_java_home is None:
        sys.stderr.write('Cannot locate new java_home\n')
        return

    old_path = os.environ['PATH'].split(':')
    clean_path = clean_up_path(old_path, java_home)
    new_path = [
        os.path.join(new_java_home, 'jre/bin'),
        os.path.join(new_java_home, 'bin'),
    ] + clean_path
    print_switch_info(new_java_home, new_path)
    print_switch_eval(new_java_home, new_path)
    return True

def print_eval_usage(argv):
    sys.stdout.write('# Please re-run using `eval` to take effect:\n')
    sys.stdout.write('#     eval "`%s`"\n' % ' '.join(argv))


if __name__ == '__main__':
    argc = len(sys.argv)
    if argc == 1:
        print_current_version()
    elif argc == 2:
        _, new_ver = sys.argv
        if switch_java_version(new_ver):
            print_eval_usage(sys.argv)
    else:
        sys.stderr.write('JVM Version Switcher: usage => jvm_switch [new_ver]')

