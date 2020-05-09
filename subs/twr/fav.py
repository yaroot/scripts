import time
import json
from TwitterAPI import TwitterAPI
from .util import timestamp_from_id, load_api
from subs import db
import logging


def request_fav(api: TwitterAPI, max_id=None):
    r = api.request('favorites/list', params={
        'count': 200,
        'max_id': max_id,
        'include_entities': 'true',
    })
    return r.json()


def save_latest():
    api = load_api()
    ts = request_fav(api)
    for t in ts:
        save_tweet(t)
    logging.info('saved %s tweets', len(ts))


def save_history():
    api = load_api()
    max_id = None
    while True:
        logging.info('max_id=%s', max_id)
        tweets = request_fav(api, max_id)
        logging.info('fetched %s tweets', len(tweets))
        if not tweets: return
        for t in tweets:
            save_tweet(t)
        logging.info('saved %s tweets', len(tweets))
        new_max_id = int(tweets[-1]['id_str'])
        if max_id == new_max_id: return
        max_id = new_max_id
        time.sleep(15)


def save_tweet(t):
    id = int(t['id_str'])
    created_at = int(timestamp_from_id(id))
    db.query(
        ''' insert into fav_tweets (id, tweet, created_at)
            values (:id, :tweet, to_timestamp(:created_at))
            on conflict (id) do update
            set tweet = :tweet
        ''',
        id=id,
        tweet=json.dumps(t),
        created_at=created_at
    )


