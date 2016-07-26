#!/usr/bin/env python3

from __future__ import print_function, division, unicode_literals
import os
import requests

BINTRAY_SECRET = os.environ['BINTRAY_SECRET']
BINTRAY_USER = os.environ['BINTRAY_USER']

assert BINTRAY_SECRET and BINTRAY_USER

BINTRAY_ENDPOINT = 'https://bintray.com/api/v1'

http_sess = requests.session()
http_sess.auth = (BINTRAY_USER, BINTRAY_SECRET)


def usage():
    print("""
    sub-commands:
        repos  <user>
        pkgs   <user> <repo>
        pkg-vers  <user> <repo> <pkg>
        pkg-files <user> <repo> <pkg>
        pkg-ver-files <user> <repo> <pkg> <ver>
        del-ver <user> <repo> <pkg> [<ver> ...]
        del-file <user> <repo> [<path> ...]
    """)

"""
Get Repositories
GET /repos/:subject

Get Packages
GET /repos/:subject/:repo/packages

Get Package (versions)
GET /packages/:subject/:repo/:package

Delete Version
DELETE /packages/:subject/:repo/:package/versions/:version

Get Package Files
GET /packages/:subject/:repo/:package/files

Get Version Files
GET /packages/:subject/:repo/:package/versions/:version/files

Delete Content
DELETE /content/:subject/:repo/:file_path
"""


def main():
    import sys
    if len(sys.argv) < 2:
        usage()
        return
    cmd, rest = sys.argv[1:]
    print(cmd, rest)

if __name__ == '__main__':
    main()

