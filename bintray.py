#!/usr/bin/env python3

from __future__ import print_function, division, unicode_literals
import os
import requests
import json

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
    pkgs   <user>/<repo>
    pkg-vers  <user>/<repo>/<pkg>
    pkg-ver  <user>/<repo>/<pkg>/<ver>
    pkg-files <user>/<repo>/<pkg>
    pkg-ver-files <user>/<repo>/<pkg>/<ver>
    del-ver   <user>/<repo>/<pkg> [<ver> ...]
    del-file  <user>/<repo> [<path> ...]
    """)


def seg_check(inp, times):
    assert inp.count('/') == times-1, "input should contain %d segment(s): %s" % (times, inp)


def pretty_dump_json(inp):
    print(json.dumps(inp, indent=True))

def request(verb, *args, **kwargs):
    r = http_sess.request(
        verb,
        '/'.join([BINTRAY_ENDPOINT] + list(args)),
        **kwargs
    )
    if r.ok:
        return r.json()


def get(*args, **kwargs):
    return request('GET', *args, **kwargs)


def delete(*args, **kwargs):
    return request('DELETE', *args, **kwargs)


def repos(user):
    """
    Get Repositories
    GET /repos/:subject
    """
    seg_check(user, 1)
    result = get('repos', user)
    for repo in result:
        print('%s/%s' % (repo['owner'], repo['name']))


def pkgs(user_repo):
    """
    Get Packages
    GET /repos/:subject/:repo/packages
    """
    seg_check(user_repo, 2)
    result = get('repos', user_repo, 'packages')
    for pkg in result:
        print('%s/%s' % (user_repo, pkg['name']))


def pkg_vers(user_repo_pkg):
    """
    Get Package (versions)
    GET /packages/:subject/:repo/:package
    """
    seg_check(user_repo_pkg, 3)
    result = get('packages', user_repo_pkg)
    for ver in result['versions']:
        print('%s/%s' % (user_repo_pkg, ver))


def pkg_ver(user_repo_pkg_ver):
    """
    Get Version
    GET / packages /:subject /:repo /:package / versions /:version
    """
    seg_check(user_repo_pkg_ver, 4)
    user, repo, pkg, ver = user_repo_pkg_ver.split('/')
    result = get('packages', user, repo, pkg, 'versions', ver)
    pretty_dump_json(result)


def pkg_files(user_repo_pkg):
    """
    Get Package Files
    GET /packages/:subject/:repo/:package/files
    """
    seg_check(user_repo_pkg, 3)
    result = get('packages', user_repo_pkg, 'files')
    pretty_dump_json(result)


def pkg_ver_files(user_repo_pkg_ver):
    """
    Get Version Files
    GET /packages/:subject/:repo/:package/versions/:version/files
    """
    seg_check(user_repo_pkg_ver, 4)
    user, repo, pkg, ver = user_repo_pkg_ver.split('/')
    result = get('packages', user, repo, pkg, 'versions', ver, 'files')
    pretty_dump_json(result)


def del_ver(user_repo_pkg, *vers):
    """
    Delete Version
    DELETE /packages/:subject/:repo/:package/versions/:version
    """
    seg_check(user_repo_pkg, 3)
    for ver in vers:
        print('Deleting <%s/%s>' % (user_repo_pkg, ver))
        result = delete('packages', user_repo_pkg, 'versions', ver)
        pretty_dump_json(result)


def del_file(user_repo, *fps):
    """
    Delete Content
    DELETE /content/:subject/:repo/:file_path
    """
    seg_check(user_repo, 2)
    for fp in fps:
        print('Deleting <%s:%s>' % (user_repo, fp))
        result = delete('content', user_repo, fp)
        pretty_dump_json(result)


def main():
    import sys
    if len(sys.argv) < 2: return usage()
    if sys.argv[1] == '-h': return usage()

    cmd, *rest = sys.argv[1:]
    if cmd == 'repos': repos(*rest)
    elif cmd == 'pkgs': pkgs(*rest)
    elif cmd == 'pkg-vers': pkg_vers(*rest)
    elif cmd == 'pkg-ver': pkg_ver(*rest)
    elif cmd == 'pkg-files': pkg_files(*rest)
    elif cmd == 'pkg-ver-files': pkg_ver_files(*rest)
    elif cmd == 'del-ver': del_ver(*rest)
    elif cmd == 'del-file': del_file(*rest)
    else:
        print('sub-command <%s> doesn\'t exist' % cmd)

if __name__ == '__main__':
    main()

