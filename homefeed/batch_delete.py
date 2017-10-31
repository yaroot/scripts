#!/usr/bin/env python

from __future__ import unicode_literals, division, print_function

import sys
import os
import re
import time
from TwitterAPI import TwitterAPI
import config


twitter = TwitterAPI(
    config.CONSUMER_KEY,
    config.CONSUMER_SECRET,
    config.ACCESS_TOKEN_KEY,
    config.ACCESS_TOKEN_SECRET
)


def delete_tweet(tid):
    print("=======")
    print('Deleting ', tid)
    r = twitter.request('statuses/destroy/:%d' % tid)
    print(r.status_code, r.get_rest_quota())


def strip_tweet_id(line):
    m = re.match('"(\d+)"', line)
    if m:
        tid, = m.groups()
        return int(tid)
    return None


def read_tweet_id(csvfile):
    with open(csvfile) as f:
        for line in f.readlines():
            yield strip_tweet_id(line)


def main():
    csvfile = sys.argv[1]
    for tweet_id in read_tweet_id(csvfile):
        if tweet_id:
            delete_tweet(tweet_id)
            time.sleep(0.3)


if __name__ == '__main__':
    main()

