#!/usr/bin/env python3
import re
import subprocess
from typing import List


SUFFIXES = ('', 'hwe')
PACKAGES = (
    'linux-headers',
    'linux-image',
    'linux-modules',
    'linux-modules-extra'
)


def exec(*cmd) -> str:
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode == 0:
        return r.stdout.decode('utf-8')
    raise RuntimeError(r.stderr.decode('utf-8'))


def current_kernel():
    return exec('uname', '-r').strip()


def contains_package_prefix(x: str):
    for p in PACKAGES:
        if x.startswith(p):
            return True
    pass


def contains_number(x: str):
    return not not re.compile(r'(\d)').findall(x)


def parse_k_version(txt: str):
    # 4.16.0-a.b.c~d.e.f
    return tuple(map(int, re.compile(r'\D').split(txt)))


def list_installed():
    all = [
        tuple(xs[1:3])
        for l in exec('dpkg', '-l').splitlines()
        for xs in [[x for x in l.split(' ') if x]]
        if xs and xs[0] == 'ii'
        if contains_package_prefix(xs[1])
        if contains_number(xs[1])
    ]
    for name, version_text in all:
        v = parse_k_version(version_text)
        yield (name, version_text, v)


def get_highest_version(versions: list):
    return sorted(versions, reverse=True)[0]


def main():
    running_ver = current_kernel()
    installed = list(list_installed())
    highest = get_highest_version([
        x
        for _, _, x in installed
    ])
    highest = highest[:5]
    print('current:', running_ver)
    print('highest:', '%d.%d.%d-%d.%d' % highest)
    to_be_removed = [
        (name, ver_txt, ver)
        for name, ver_txt, ver in installed
        if running_ver not in name
        if ver[:5] != highest
    ]

    print('kernel packages should be removed:')
    for x in to_be_removed:
        print(' ', (x[0]))
    pass


if __name__ == '__main__':
    main()
