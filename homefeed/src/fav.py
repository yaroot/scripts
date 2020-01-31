import sys
import time
import json
from TwitterAPI import TwitterAPI
import records
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
db = records.Database(f'sqlite:///./{DB_FILE}')

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


def savage_latest(twitter: TwitterAPI):
    tweets = request_fav(twitter)
    if tweets:
        for t in tweets:
            insert(t)
        print('saved %s tweets' % len(tweets))
    pass


def savage_history(twitter: TwitterAPI):
    max_id = None
    while True:
        print('max_id=%s' % max_id)
        tweets = request_fav(twitter, max_id)
        print('fetched %s tweets' % len(tweets))
        if not tweets:
            return
        for t in tweets:
            insert(t)
        print('saved %s tweets' % len(tweets))
        new_max_id = int(tweets[-1]['id_str'])
        if max_id == new_max_id:
            return
        max_id = new_max_id
        time.sleep(15)


def insert(t):
    id = int(t['id_str'])
    created_at = int(timestamp_from_id(id))
    db.query(
        '''
        INSERT INTO fav_tweets (`id`, `tweet`, `created_at`)
        VALUES (:id, :tweet, :created_at)
        ON CONFLICT (`id`) DO NOTHING
        ''',
        id=id,
        tweet=json.dumps(t),
        created_at=created_at
    )


def main():
    twitter = load_api()
    if '-h' in sys.argv:
        savage_history(twitter)
    savage_latest(twitter)


if __name__ == '__main__':
    main()

