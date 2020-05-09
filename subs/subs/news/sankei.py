import logging
import time
from datetime import datetime, timedelta, timezone
from subs import config, services

TEMPLATE = """
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>産経新聞</title>
    <link href="{{ feed_url }}/sankei.xml" rel="self" />
    <link href="{{ feed_url }}" />
    <updated>{{ last_updated }}</updated>
    <id>urn:feed:{{ feed_id }}</id>

    {{ #items }}
    <entry>
        <title><![CDATA[{{ title }}]]></title>
        <link href="{{ url }}" />
        <updated>{{ date }}</updated>
        <id>{{ id }}</id>
        <content type="html"></content>
    </entry>
    {{ /items }}
</feed>
""".strip()

NEWS_URL = 'https://www.sankei.com/json/newslist/flash.json'
AGENCY = 'sankei'


def parse_date(text):
    d = datetime.strptime(text, '%Y/%m/%d %H:%M:%S') - timedelta(hours=9)
    d = d.replace(tzinfo=timezone.utc)
    return int(d.timestamp())


def crawl_new():
    r = services.httpclient.get(NEWS_URL)
    assert not r.is_error
    articles = r.json()['article']
    logging.info('Got %d articles (%s)', len(articles), AGENCY)
    for art in articles:
        _id = art['id']
        date = art['date']
        title = art['title']
        url = art['url']
        genre = art['parent_genre_name']
        date = parse_date(date)
        services.upsert_news(
            agency=AGENCY,
            id=_id,
            title='%s: %s' % (genre, title),
            url=url,
            created_at=date,
            updated_at=date,
            desc=None
        )


def write_rss():
    articles = services.recent_news(AGENCY)
    items = [
        {
            'title': x.title,
            'url': x.url,
            'date': services.format_ts(x.updated_at),
            'id': x.id
        }
        for x in articles
    ]

    data = {
        'feed_url': config.FEED_URL,
        'feed_id': config.SANKEI_ID,
        'last_updated': services.format_ts(int(time.time())),
        'items': items,
    }
    logging.info('Writing %d feeds (%s)', len(items), AGENCY)
    services.render_pystache_to(TEMPLATE, data, 'sankei.xml')


def main():
    crawl_new()
    write_rss()

