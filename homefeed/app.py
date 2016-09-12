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

CACHE_SIZE = 1000 * 100
FEED_SIZE = 1000 * 10
CACHE_FILENAME = 'data/feed_cache.json'
FEED_FILENAME = 'data/feed.xml'

TEMPLATE_HEAD = """
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{{ FEED_TITLE }}</title>
  <link href="{{ FEED_LINK_SELF }}" rel="self" />
  <link href="{{ FEED_LINK }}" />
  <updated>{{ LAST_UPDATE }}</updated>
  <id>urn:feed:{{ FEED_ID }}</id>
  <author>
    <name>{{ FEED_AUTHOR }}</name>
  </author>
"""

TEMPLATE_BODY = """
  <entry>
    <title><![CDATA[{{ #user }}@{{ screen_name }} {{ name }}{{ /user }}: {{ text }}]]></title>
    <link href="https://mobile.twitter.com/{{ #user }}{{ screen_name }}{{ /user }}/status/{{ id_str }}" />
    <updated>{{ timestamp_isoformat }}</updated>
    <id>urn:tweet:{{ id_str }}</id>
    <content type="html">
      <![CDATA[
      {{ #extended_entities }}
        {{ #media }}
          <a href="{{ display_url }}" rel="nofollow">
            <img src="{{ media_url_https }}" alt="{{ display_url }}">
          </a>
        {{ /media }}
      {{ /extended_entities }}
      ]]>
    </content>
  </entry>
"""

TEMPLATE_CLOSING = """
</feed>
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
        if type(content) in (unicode, str):
            f.write(content)
        else:
            for chunk in content:
                f.write(chunk)
    os.rename(tmp, path)


def read_local_cache():
    if not os.path.exists(CACHE_FILENAME):
        return []
    with open(CACHE_FILENAME, 'r') as f:
        return [
            json.loads(line)
            for line in f.readlines()
        ]


def write_local_cache(tweets):
    serialized = [json.dumps(tweet) + '\n' for tweet in tweets]
    atomic_write(CACHE_FILENAME, serialized)


def produce_feed(tweets):
    to_render = keep_fitness([t for t in tweets if 'text' in t], FEED_SIZE)
    if to_render:
        rendered = (chunk.encode('utf-8') for chunk in render_feed(to_render))
        atomic_write(FEED_FILENAME, rendered)


def main_loop(tweets, twitter):
    for item in twitter.request('user'):
        tweets.append(item)
        tweets = keep_fitness(tweets, CACHE_SIZE)
        trywith(lambda: write_local_cache(tweets))
        trywith(lambda: produce_feed(tweets))


def main():
    cached_tweets = read_local_cache()
    twitter = TwitterAPI(
        config.CONSUMER_KEY,
        config.CONSUMER_SECRET,
        config.ACCESS_TOKEN_KEY,
        config.ACCESS_TOKEN_SECRET)

    import time
    while True:
        trywith(lambda: main_loop(cached_tweets, twitter))
        time.sleep(1)


if __name__ == '__main__':
    main()
