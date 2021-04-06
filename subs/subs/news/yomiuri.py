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

NEWS_URL1 = 'https://www.yomiuri.co.jp/y_ajax/latest_list_news/category/2,54,48,47,1538,2277/0/1/0/1939/20/?action=latest_list_news&others=category%2F2%2C54%2C48%2C47%2C1538%2C2277%2F0%2F1%2F0%2F1939%2F20%2F'
NEWS_URL2 = 'https://www.yomiuri.co.jp/y_ajax/latest_list_news2/category/2,54,48,47,1538,2277/0/1/20/1939/30/?action=latest_list_news2&others=category%2F2%2C54%2C48%2C47%2C1538%2C2277%2F0%2F1%2F20%2F1939%2F30%2F'


def capitalize(x: str):
    "local -> Local"
    return x[0].upper() + x[1:]


def crawl_new():
    c = 0
    for crawl_url in (NEWS_URL1, NEWS_URL2):
        r = services.httpclient.get(crawl_url)
        assert not r.is_error
        dom = lxml.html.fromstring(r.text)
        for article in dom.getchildren():
            a = article.cssselect('h3 a')[0]
            url = a.attrib['href']
            title = a.text_content()
            time_text = article.cssselect('time')[0].attrib['datetime']
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

