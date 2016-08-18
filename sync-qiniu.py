#!/usr/bin/env python3

from __future__ import unicode_literals, division
import requests as _requests
import hmac
from hashlib import sha1
from base64 import urlsafe_b64encode
import logging
from urllib.parse import urlparse

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


def main():
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='sync qiniu')
    print(urlparse('qiniu://bucket/pathxxxxx'))
    pass

if __name__ == '__main__':
    main()
