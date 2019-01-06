#!/usr/bin/env python

from __future__ import unicode_literals, division

import json
import os
from datetime import datetime
from TwitterAPI import TwitterAPI
import pystache
import config
import logging as _logger_factory
_logger_factory.basicConfig(
    level=_logger_factory.DEBUG,
    format='%(levelname)-5s %(asctime)s %(name)s %(message)s'
)

logger = _logger_factory.getLogger(__name__)

TIMELINE_SIZE = 1000 * 3
CACHE_FILENAME = 'data/feed_cache.json'
FEED_FILENAME = 'data/feed.json'


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
def format_timestamp_millis(i):
    return format_timestamp_seconds(int(i) / 1000)


def format_timestamp_seconds(i):
    return datetime.utcfromtimestamp(int(i)).isoformat() + 'Z'


def reformat_timestamp(tweet):
    copy = dict(tweet)
    copy['timestamp_isoformat'] = format_timestamp_millis(tweet['timestamp_ms'])
    return copy


def render_feed(tweets):
    assert len(tweets) > 0
    header_data = {
        'LAST_UPDATE': format_timestamp_millis(tweets[-1]['timestamp_ms']),
        'FEED_TITLE': config.FEED_TITLE,
        'FEED_LINK_SELF': config.FEED_LINK_SELF,
        'FEED_LINK': config.FEED_LINK,
        'FEED_ID': config.FEED_ID,
        'FEED_AUTHOR': config.FEED_AUTHOR,
    }
    yield pystache.render(TEMPLATE_HEAD, header_data)
    for t in reversed(tweets):
        yield pystache.render(TEMPLATE_BODY, reformat_timestamp(t))
    yield TEMPLATE_CLOSING


def trywith(f):
    try:
        f()
    except MemoryError:
        logger.exception('memory error, exiting')
        import sys
        sys.exit(-1)
    except Exception:
        logger.exception('exception occurred')


def keep_fitness(lst, max_size):
    if len(lst) > max_size:
        return lst[len(lst) - max_size:]
    else:
        return lst


def atomic_write(path, content):
    tmp = '{}.tmp'.format(path)
    with open(tmp, 'w') as f:
        f.write(content)
    os.rename(tmp, path)


def write_cache(tweets):
    atomic_write(CACHE_FILENAME, json.dumps(tweets))


def write_feed(tweets):
    pass


def fetch_tweets0(twitter: TwitterAPI, since_id=None):
    pass


def fetch_tweets(twitter: TwitterAPI, since_id=None):
    params = {
        'count': 200,
        'since_id': since_id
    }
    r = twitter.request('statuses/home_timeline', params)
    import ipdb; ipdb.set_trace()
    pass


def load_old_tweets():
    if os.path.exists(CACHE_FILENAME):
        with open(CACHE_FILENAME) as f:
            return json.loads(f.read())
    else:
        return []


def main():
    twitter = TwitterAPI(
        config.CONSUMER_KEY,
        config.CONSUMER_SECRET,
        config.ACCESS_TOKEN_KEY,
        config.ACCESS_TOKEN_SECRET)

    old_tweets = load_old_tweets()
    new_tweets = fetch_tweets(twitter)
    # merge tweets
    # write feed
    # write cache


if __name__ == '__main__':
    main()
