import sys
import time
import json
from TwitterAPI import TwitterAPI
import sqlite3
from .util import timestamp_from_id, load_api

import logging as _logger_factory
_logger_factory.basicConfig(
    level=_logger_factory.INFO,
    format='%(levelname)-5s %(asctime)s %(name)s %(message)s',
    stream=sys.stdout
)

logger = _logger_factory.getLogger('fav')
DB_FILE = 'fav.sqlite'
DB_EXPORT = 'fav.sql'

SCHEMA = """
CREATE TABLE IF NOT EXISTS "fav_tweets" (
 `id` UNSIGNED INTEGER NOT NULL PRIMARY KEY,
 `tweet` TEXT NOT NULL,
 `created_at` UNSIGNED INTEGER NOT NULL
);
"""


def request_fav(twitter: TwitterAPI, max_id=None):
    r = twitter.request('favorites/list', params={
        'count': 200,
        'max_id': max_id,
        'include_entities': 'true',
    })
    return r.json()


def savage_latest(twitter: TwitterAPI, db: sqlite3.Connection):
    tweets = request_fav(twitter)
    if tweets:
        for t in tweets:
            insert(db, t)
        print('saved %s tweets' % len(tweets))
    pass


def savage_history(twitter: TwitterAPI, db: sqlite3.Connection):
    max_id = None
    while True:
        print('max_id=%s' % max_id)
        tweets = request_fav(twitter, max_id)
        print('fetched %s tweets' % len(tweets))
        if not tweets:
            return
        for t in tweets:
            insert(db, t)
        print('saved %s tweets' % len(tweets))
        new_max_id = int(tweets[-1]['id_str'])
        if max_id == new_max_id:
            return
        max_id = new_max_id
        time.sleep(3)


def dump_db(db: sqlite3.Connection):
    with open(DB_EXPORT, 'w') as f:
        for l in db.iterdump():
            f.write(l)
            f.write('\n')
    pass


def open_db():
    db = sqlite3.connect(DB_FILE)
    db.cursor().execute(SCHEMA).close()
    return db


def insert(db: sqlite3.Connection, t):
    id = int(t['id_str'])
    created_at = int(timestamp_from_id(id))
    cur = db.cursor()
    cur.execute(
        """
        INSERT INTO fav_tweets (`id`, `tweet`, `created_at`)
        VALUES (?, ?, ?)
        ON CONFLICT (`id`) DO NOTHING
        """,
        (id, json.dumps(t), created_at)
    )
    db.commit()
    cur.close()


def load_max_id(db: sqlite3.Connection):
    cur = db.cursor()
    cur.execute('select min(id) from fav_tweets')
    r = cur.fetchone()
    db.rollback()
    cur.close()
    if r:
        return r[0]
    pass


def main():
    twitter = load_api()
    db = open_db()
    if '-h' in sys.argv:
        savage_history(twitter, db)
    savage_latest(twitter, db)

    dump_db(db)
    db.close()


if __name__ == '__main__':
    main()

