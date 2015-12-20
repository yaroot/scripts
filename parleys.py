#!/usr/bin/env python2
# code=utf-8

from __future__ import unicode_literals

import sys
import requests
import logging
import re
from urlparse import urlparse
import subprocess


def download(url, filename):
    cmd = ['curl', url, '--output', filename]
    logging.info('Starting [%s]', ' '.join(cmd))
    subprocess.call(cmd, stderr=sys.stderr, stdin=sys.stdin, stdout=sys.stdout)


def parse_video_id(url):
    parsed = urlparse(url)
    return re.match(r'^/tutorial/([^/]+)$', parsed.path).groups()[0]


def parse_downloadable_medias(details):
    assets = [asset for asset in details['assets'] if asset['target'] == 'STREAM']
    slug = details['slug']
    sequence = 0
    for asset in assets:
        for f in asset['files']:
            sequence += 1
            ext = f['format']
            url = f['httpDownloadURL']
            download(url, '%s-%d.%s' % (slug, sequence, ext.lower()))


def request_media_files(video_id):
    details = requests.get('https://api.parleys.com/api/presentation.json/%s' % video_id)
    return parse_downloadable_medias(details.json())


def main(url):
    try:
        video_id = parse_video_id(url)
        if not video_id:
            logging.error('invalid video url: %s', url)
            return
        request_media_files(video_id)
    except Exception:
        logging.exception('error downloading %s', url)



if __name__ == '__main__':
    map(main, sys.argv[1:])
