import lxml.html
import lxml.etree
import logging
import time
from datetime import datetime, timedelta, timezone
from subs import config, services
from urllib.parse import urlparse


TEMPLATE = """
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>読売新聞</title>
    <link href="{{ feed_url }}/yomiuri.xml" rel="self" />
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

NEWS_URL = 'https://www.yomiuri.co.jp/news/'
AGENCY = 'yomiuri'


def capitalize(x: str):
    "local -> Local"
    return x[0].upper() + x[1:]


def crawl_new():
    c = 0
    r = services.httpclient.get(NEWS_URL)
    assert not r.is_error
    dom = lxml.html.fromstring(r.text)
    news_ul = dom.cssselect('ul.news-top-upper-content-latest-content-list')[0]
    for li in news_ul.getchildren():
        a = li.cssselect('h3 a')[0]
        url = a.attrib['href']
        title = a.text_content()
        time_text = li.cssselect('time')[0].attrib['datetime']
        u = urlparse(url)
        publish_time = datetime.strptime(time_text, '%Y-%m-%dT%H:%M') - timedelta(hours=9)
        publish_time = publish_time.replace(tzinfo=timezone.utc).timestamp()
        publish_time = int(publish_time)
        segments = [x for x in u.path.split('/') if x]
        _id = segments[-1]
        genre = segments[0]
        title = '[%s]%s' % (capitalize(genre), title)

        c += 1
        services.upsert_news(
            agency=AGENCY,
            id=_id,
            title=title,
            url=url,
            desc=None,
            created_at=publish_time,
            updated_at=publish_time,
        )
    logging.info('Got %d news (%s)', c, AGENCY)


def write_rss():
    items = [
        {
            'title': x.title,
            'url': x.url,
            'date': services.format_ts(x.updated_at),
            'id': x.id,
        }
        for x in services.recent_news(AGENCY, 30)
    ]
    data = {
        'feed_url': config.FEED_URL,
        'feed_id': config.YOMIURI_ID,
        'last_updated': services.format_ts(int(time.time())),
        'items': items,
    }
    logging.info('Wrote %d feeds (%s)', len(items), AGENCY)
    services.render_pystache_to(TEMPLATE, data, 'yomiuri.xml')


def main():
    crawl_new()
    write_rss()

