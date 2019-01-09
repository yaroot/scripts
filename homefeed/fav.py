import sys
import time
import json
import os
from datetime import datetime
from TwitterAPI import TwitterAPI
import config
import sqlite3

import logging as _logger_factory
_logger_factory.basicConfig(
    level=_logger_factory.INFO,
    format='%(levelname)-5s %(asctime)s %(name)s %(message)s',
    stream=sys.stdout
)

logger = _logger_factory.getLogger('fav')
DB_FILE = 'fav.sqlite'
DB_EXPORT = 'fav.sql'


def load_history(twitter: TwitterAPI, db: sqlite3.Connection):
    r = twitter.request('favorites/list', params={
        'count': 20,
        'max_id': None,
        'include_entities': 'true',
    })
    import ipdb; ipdb.set_trace()
    pass


def dump_db(db: sqlite3.Connection):
    with open(DB_EXPORT) as f:
        for l in db.iterdump():
            f.write(l)
            f.write('\n')
    pass


def main():
    twitter = TwitterAPI(
        config.CONSUMER_KEY,
        config.CONSUMER_SECRET,
        config.ACCESS_TOKEN_KEY,
        config.ACCESS_TOKEN_SECRET)
    db = sqlite3.connect(DB_FILE)
    load_history(twitter, db)

    # dump_db(db)

if __name__ == '__main__':
    main()

