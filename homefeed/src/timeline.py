#!/usr/bin/env python

import sys
import time
import json
import os
from datetime import datetime, timezone
from TwitterAPI import TwitterAPI
from . import config
import logging as _logger_factory
from .util import timestamp_from_id, load_api
import pystache

_logger_factory.basicConfig(
    level=_logger_factory.INFO,
    format='%(levelname)-5s %(asctime)s %(name)s %(message)s',
    stream=sys.stdout
)

logger = _logger_factory.getLogger('homefeed')

TIMELINE_SIZE = 500
FETCH_COUNT = 200

CACHE_FILENAME = 'data/feed_cache.json'
FEED_FILENAME = 'data/feed.xml'


def read_template():
    base = os.path.dirname(__file__)
    tp = os.path.join(base, 'feed_template.xml')
    with open(tp) as f:
        return f.read()


FEED_TEMPLATE = read_template()

# tweet example
"""
{
  "created_at": "Sun Jan 06 10:01:53 +0000 2019",
  "id": 1081853350054785000,
  "id_str": "1081853350054785025",
  "text": "说好的\"Full Support for Windows Server 2019\"呢？ https://t.co/MUIUtevvLF",
  "truncated": false,
  "entities": {
    "hashtags": [],
    "symbols": [],
    "user_mentions": [],
    "urls": [],
    "media": [
      {
        "id": 1081853239153197000,
        "id_str": "1081853239153197056",
        "indices": [
          44,
          67
        ],
        "media_url": "http://pbs.twimg.com/media/DwODygLVAAAvlcB.jpg",
        "media_url_https": "https://pbs.twimg.com/media/DwODygLVAAAvlcB.jpg",
        "url": "https://t.co/MUIUtevvLF",
        "display_url": "pic.twitter.com/MUIUtevvLF",
        "expanded_url": "https://twitter.com/nekomplex/status/1081853350054785025/photo/1",
        "type": "photo",
        "sizes": {
          "large": {
            "w": 1425,
            "h": 834,
            "resize": "fit"
          },
          "thumb": {
            "w": 150,
            "h": 150,
            "resize": "crop"
          },
          "small": {
            "w": 680,
            "h": 398,
            "resize": "fit"
          },
          "medium": {
            "w": 1200,
            "h": 702,
            "resize": "fit"
          }
        }
      }
    ]
  },
  "extended_entities": {
    "media": [
      {
        "id": 1081853239153197000,
        "id_str": "1081853239153197056",
        "indices": [
          44,
          67
        ],
        "media_url": "http://pbs.twimg.com/media/DwODygLVAAAvlcB.jpg",
        "media_url_https": "https://pbs.twimg.com/media/DwODygLVAAAvlcB.jpg",
        "url": "https://t.co/MUIUtevvLF",
        "display_url": "pic.twitter.com/MUIUtevvLF",
        "expanded_url": "https://twitter.com/nekomplex/status/1081853350054785025/photo/1",
        "type": "photo",
        "sizes": {
          "large": {
            "w": 1425,
            "h": 834,
            "resize": "fit"
          },
          "thumb": {
            "w": 150,
            "h": 150,
            "resize": "crop"
          },
          "small": {
            "w": 680,
            "h": 398,
            "resize": "fit"
          },
          "medium": {
            "w": 1200,
            "h": 702,
            "resize": "fit"
          }
        }
      }
    ]
  },
  "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>",
  "in_reply_to_status_id": null,
  "in_reply_to_status_id_str": null,
  "in_reply_to_user_id": null,
  "in_reply_to_user_id_str": null,
  "in_reply_to_screen_name": null,
  "user": {
    "id": 78234516,
    "id_str": "78234516",
    "name": "猫爺划水中",
    "screen_name": "nekomplex",
    "location": "Nagoya, Japan",
    "description": "博土临时工／无薪程序员／桥洞投资家／岛国吃瓜党／资深魔法师／微笑真任饭／",
    "url": null,
    "entities": {
      "description": {
        "urls": []
      }
    },
    "protected": false,
    "followers_count": 477,
    "friends_count": 635,
    "listed_count": 10,
    "created_at": "Tue Sep 29 06:20:54 +0000 2009",
    "favourites_count": 559,
    "utc_offset": null,
    "time_zone": null,
    "geo_enabled": true,
    "verified": false,
    "statuses_count": 7362,
    "lang": "en",
    "contributors_enabled": false,
    "is_translator": false,
    "is_translation_enabled": false,
    "profile_background_color": "C0DEED",
    "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
    "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
    "profile_background_tile": false,
    "profile_image_url": "http://pbs.twimg.com/profile_images/606390618428837888/X4-SDIX4_normal.jpg",
    "profile_image_url_https": "https://pbs.twimg.com/profile_images/606390618428837888/X4-SDIX4_normal.jpg",
    "profile_banner_url": "https://pbs.twimg.com/profile_banners/78234516/1434628625",
    "profile_link_color": "1DA1F2",
    "profile_sidebar_border_color": "C0DEED",
    "profile_sidebar_fill_color": "DDEEF6",
    "profile_text_color": "333333",
    "profile_use_background_image": true,
    "has_extended_profile": false,
    "default_profile": true,
    "default_profile_image": false,
    "following": true,
    "follow_request_sent": false,
    "notifications": false,
    "translator_type": "none"
  },
  "geo": null,
  "coordinates": null,
  "place": null,
  "contributors": null,
  "is_quote_status": false,
  "retweet_count": 0,
  "favorite_count": 0,
  "favorited": false,
  "retweeted": false,
  "possibly_sensitive": false,
  "possibly_sensitive_appealable": false,
  "lang": "zh"
}
"""


def get_zulu_time(t):
    ts = timestamp_from_id(t['id'])
    dt = datetime.utcfromtimestamp(ts)
    return format_time(dt)


def format_time(dt):
    return dt.isoformat() + 'Z'


def get_image_content_html(t):
    media = t.get('extended_entities', {}).get('media', [])
    return '\n<br>\n'.join([
        '''<a href="{link}" rel="nofollow"><img src="{src}"></a>'''.format(
            link=img['url'], src=img['media_url_https'])
        for img in media
    ])


def generate_timeline(tweets):
    return [
        {
            'id': 'urn:tweet:{}'.format(t['id']),
            'title': '{} (@{}): {}'.format(t['user']['name'], t['user']['screen_name'], t['text']),
            'url': 'https://mobile.twitter.com/{}/status/{}'.format(t['user']['screen_name'], t['id']),
            'date_published': get_zulu_time(t),
            # 'date_modified': format_time(datetime.utcnow()),
            'content_html': html if html else None
        }
        for t in tweets
        for html in [get_image_content_html(t)]
    ]


def pretty_json(xs):
    return json.dumps(xs, ensure_ascii=True, indent=2)


def atomic_write(path, data: str):
    tmp = '{}.tmp'.format(path)
    with open(tmp, 'w') as f:
        f.write(data)
    os.rename(tmp, path)


def write_cache(tweets):
    atomic_write(CACHE_FILENAME, pretty_json(tweets))


def write_feed(tweets):
    data = {
        'version': 'https://jsonfeed.org/version/1',
        'feed_id': config.FEED_ID,
        'feed_url': config.FEED_URL,
        'title': config.FEED_TITLE,
        'last_updated': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        'home_page_url': 'https://twitter.com/',
        'items': generate_timeline(tweets),
    }

    rendered = pystache.render(
        pystache.parse(FEED_TEMPLATE),
        context=data
    )
    atomic_write(FEED_FILENAME, rendered)


# def write_feed(tweets):
    # data = {
    #     'version': 'https://jsonfeed.org/version/1',
    #     'title': config.FEED_TITLE,
    #     'home_page_url': 'https://twitter.com/',
    #     'items': generate_timeline(tweets)
    # }
    # atomic_write_json(FEED_FILENAME, data)


def fetch_tweets0(twitter: TwitterAPI, since_id=None):
    params = {
        'count': FETCH_COUNT,
        'since_id': since_id
    }
    r = twitter.request('statuses/home_timeline', params)
    tweets = r.json()
    new_since_id = None
    if tweets:
        new_since_id = tweets[0]['id']
    return tweets, new_since_id


def fetch_tweets(twitter: TwitterAPI, since_id=None):
    tweets = []
    while True:
        tweets0, new_id = fetch_tweets0(twitter, since_id)
        tweets = tweets0 + tweets
        logger.info('fetched {} new tweets, new_id={}, old_id={}'.format(len(tweets0), since_id, new_id))
        if len(tweets) < FETCH_COUNT/2 or not new_id:
            return tweets
        since_id = new_id
        time.sleep(1)


def load_old_tweets():
    if os.path.exists(CACHE_FILENAME):
        with open(CACHE_FILENAME) as f:
            return json.loads(f.read())
    else:
        return []


def main():
    twitter = load_api()

    old_tweets = load_old_tweets()
    logger.info('loaded {} old tweets'.format(len(old_tweets)))
    since_id = old_tweets[0]['id'] if old_tweets else None
    new_tweets = fetch_tweets(twitter, since_id)
    logger.info('loaded {} new tweets'.format(len(new_tweets)))

    all_tweets = new_tweets + old_tweets
    # all_tweets = old_tweets
    write_cache(all_tweets[:TIMELINE_SIZE])
    write_feed(all_tweets)
    logger.info('written {} items'.format(len(all_tweets)))


if __name__ == '__main__':
    main()
