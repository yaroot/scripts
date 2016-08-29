#!/usr/bin/env python3

# http://developer.qiniu.com/article/index.html

from __future__ import unicode_literals, division
import requests as _requests
import hmac
from hashlib import sha1
from base64 import urlsafe_b64encode
import logging
from path import Path

# global pool
requests = _requests.session()


class AuthKey(object):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def sign(self, path, query, body=''):
        digest = hmac.new(self.secret, path+query+'\n'+body, sha1).digest()
        return urlsafe_b64encode(digest)


def retry(max_retry=3):
    def _retry(f, *args, **kwargs):
        n = max_retry
        while n > 0:
            try:
                return f(*args, **kwargs)
            except:
                logging.exception("error executing " + f)
            n -= 1
    return _retry


def joinpath(*args):
    agg = ''
    for seg in args:
        if agg == '':
            # first one, preserve `/` in the left
            agg += seg
        else:
            agg += '/'
            agg += seg.lstrip('/')
    return agg


class Storage(object):
    @staticmethod
    def new_qiniu(url):
        return QiniuStorage(url)

    @staticmethod
    def new_local(url):
        return LocalStorage(url)

    def scan(self):
        pass
    pass


class LocalStorage(Storage):
    def __init__(self, url):
        self.basepath = url
        self.filelist = self.scan()

    def scan(self):
        pass


class QiniuStorage(Storage):
    def __init__(self, url):
        bucket, basepath = url.split('/', 1)
        self.bucket = bucket
        self.basepath = basepath
        self.filelist = self.scan()

    def scan(self):
        pass


class FileObject(object):
    pass


class LocalObject(FileObject):
    pass


class QiniuObject(FileObject):
    pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description='sync qiniu')
    parser.add_argument('action', type=str, help='upload / download')
    parser.add_argument('source', type=str, help='local path or `<bucket>/optional/path`')
    parser.add_argument('target', type=str, help='same with source, one should be local path, the other should be remote url')
    parser.add_argument('-f', metavar='force', type=bool, default=False)
    parser.add_argument('-d', metavar='delete', type=bool, default=False)
    args = parser.parse_args()
    print(args)
    pass

if __name__ == '__main__':
    main()
