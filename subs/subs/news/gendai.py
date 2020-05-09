from datetime import datetime
import logging
import time
import pystache
import lxml.html
import lxml.etree
import json
from dateutil.parser import parse as parse_dt
import pytz
from subs import services, config


TEMPLATE = """
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>日刊ゲンダイ</title>
    <link href="{{ feed_url }}/gendai.xml" rel="self" />
    <link href="{{ feed_url }}" />
    <updated>{{ last_updated }}</updated>
    <id>urn:feed:{{ feed_id }}</id>

    {{ #items }}
    <entry>
        <title><![CDATA[{{ title }}]]></title>
        <link href="{{ url }}" />
        <updated>{{ date }}</updated>
        <id>{{ id }}</id>
        <content type="html"><![CDATA[{{ desc }}]]></content>
    </entry>
    {{ /items }}
</feed>
""".strip()

BASE_URL = 'https://www.nikkan-gendai.com'
AGENCY = 'gendai'


def parse_time(text: str):
    return int(parse_dt(text).timestamp())


def parse_id(url: str):
    i = url.rfind('/')
    return url[i+1:]


def crawl_article(url: str):
    r = services.httpclient.get(url, allow_redirects=True)
    assert r.status_code == 200
    dom = lxml.html.fromstring(r.content)
    schema = dom.cssselect('script[type="application/ld+json"]')
    if not schema: return
    schema = schema[0]
    schema = json.loads(schema.text)
    url = schema['mainEntityOfPage']['@id']
    title = schema['headline']
    desc = schema['description']
    created_at = parse_time(schema['datePublished'])
    updated_at = parse_time(schema['dateModified'])
    id = parse_id(url)
    services.upsert_news(
        agency=AGENCY,
        id=id,
        url=url,
        title=title,
        desc=desc,
        created_at=created_at,
        updated_at=updated_at,
    )


def crawl_rss():
    c = 0
    r = services.httpclient.get(BASE_URL)
    assert r.status_code == 200
    dom = lxml.html.fromstring(r.content)
    xs = dom.cssselect('a[href]')
    for x in xs:
        href = x.attrib['href']
        if '/articles/view/' not in href: continue
        url = f'{BASE_URL}{href}' if href.startswith('/') else href
        articles = services.news_by_url(AGENCY, url)
        if not articles:
            crawl_article(url)
            c += 1
    logging.info('Got %d new articles (%s)', c, AGENCY)


def write_rss():
    items = [
        {
            'title': x.title,
            'url': x.url,
            'date': services.format_ts(x.updated_at),
            'id': x.id,
            'desc': x.desc,
        }
        for x in services.recent_news(AGENCY, 30)
    ]
    data = {
        'feed_url': config.FEED_URL,
        'feed_id': config.SANKEI_ID,
        'last_updated': services.format_ts(int(time.time())),
        'items': items,
    }
    logging.info('Writing %d feeds (%s)', len(items), AGENCY)
    services.render_pystache_to(TEMPLATE, data, 'gendai.xml')


def main():
    crawl_rss()
    write_rss()

