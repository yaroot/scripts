#!/usr/bin/env python2
"""
dump image list from v1 registry for migration
if you need more features please use https://github.com/docker/migrator

v2 registry doesn't support search endpoint yet
"""

from __future__ import print_function, unicode_literals, division

import sys
import requests

session = requests.session()


def dump_all_images(base_url):
    r = session.get("%s/v1/search" % base_url)
    for image in r.json()['results']:
        yield image['name']


def dump_all_tags(base_url, image):
    r = session.get("%s/v1/repositories/%s/tags" % (base_url, image))
    for tag, _ in r.json().items():
        yield tag


def dump_all_images_with_tags(registry_base):
    sys.stderr.write('> fetching image list\n')
    for image in dump_all_images(registry_base):
        sys.stderr.write('> fetching tags for %s\n' % image)
        for tag in dump_all_tags(registry_base, image):
            sys.stdout.write('%s:%s\n' % (image, tag))


def main():
    if len(sys.argv) == 2:
        dump_all_images_with_tags(sys.argv[1].rstrip("/"))
    else:
        print("Usage: dump.py http(s)://your.registry:port")

if __name__ == '__main__':
    main()
