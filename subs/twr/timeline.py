#!/usr/bin/env python

import time
import json
from datetime import datetime
from TwitterAPI import TwitterAPI
import logging
from .util import timestamp_from_id, load_api
from subs import config, db, services


TIMELINE_SIZE = 100
FETCH_COUNT = 200


FEED_TEMPLATE = """
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{{ title }}</title>
    <link href="{{ feed_url }}/feed.xml" rel="self" />
    <link href="{{ feed_url }}" />
    <updated>{{ last_updated }}</updated>
    <id>urn:feed:{{ feed_id }}</id>

    {{ #items }}
    <entry>
        <title><![CDATA[{{ title }}]]></title>
        <link href="{{ url }}" />
        <updated>{{ date_published }}</updated>
        <id>{{ id }}</id>
        <content type="html">
            {{ #content_html }}
            <![CDATA[{{& content_html }}]]>
            {{ /content_html }}
        </content>
    </entry>
    {{ /items }}
</feed>
""".strip()

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
    return services.format_ts(ts)


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
            'content_html': html if html else None
        }
        for t in tweets
        for html in [get_image_content_html(t)]
    ]


def save(t):
    _id = t['id']
    with db.transaction():
        db.query(
            'insert into timeline_tweets (id, tweet, created_at)'
            'values (:id, :tweet, to_timestamp(:created_at))'
            'on conflict (id) do update set tweet = :tweet',
            id=_id,
            tweet=json.dumps(t),
            created_at=timestamp_from_id(_id)
        )
    pass


def write_feed(tweets):
    data = {
        'feed_id': config.FEED_ID,
        'feed_url': config.FEED_URL,
        'title': config.FEED_TITLE,
        'last_updated': services.format_ts(time.time()),
        'home_page_url': 'https://twitter.com/',
        'items': generate_timeline(tweets),
    }

    services.render_pystache_to(FEED_TEMPLATE, data, 'feed.xml')


def fetch_tweets0(api: TwitterAPI, since_id=None):
    params = {
        'count': FETCH_COUNT,
        'since_id': since_id
    }
    r = api.request('statuses/home_timeline', params)
    tweets = r.json()
    new_since_id = None
    if tweets:
        new_since_id = tweets[0]['id']
    return tweets, new_since_id


def fetch_tweets(api: TwitterAPI, since_id=None):
    tweets = []
    while True:
        tweets0, new_id = fetch_tweets0(api, since_id)
        tweets = tweets0 + tweets
        logging.info('fetched {} new tweets, new_id={}, old_id={}'.format(len(tweets0), since_id, new_id))
        if len(tweets) < FETCH_COUNT/2 or not new_id:
            return tweets
        since_id = new_id
        time.sleep(1)


def load_oldest_id():
    with db.transaction():
        xs = db.query('select * from timeline_tweets order by id desc limit 1').all()
        if xs: return xs[0].id


def recent_tweets(size):
    with db.transaction():
        return db.query('select * from timeline_tweets order by id desc limit :size', size=size).all()


def main():
    api = load_api()

    since_id = load_oldest_id()

    logging.info('request new tweets since_id=%s', since_id)
    new_tweets = fetch_tweets(api, since_id)
    logging.info('loaded %s new tweets', len(new_tweets))
    for t in new_tweets:
        save(t)

    tweets = recent_tweets(TIMELINE_SIZE)
    write_feed([t.tweet for t in tweets])
    logging.info('written {} items'.format(len(tweets)))

