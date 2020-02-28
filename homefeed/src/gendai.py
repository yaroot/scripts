import httpx
import records
from datetime import datetime
import logging
import time
import pystache
import lxml.html
import lxml.etree
import json
from dateutil.parser import parse as parse_dt
import pytz
from . import config


SCHEMA = '''
create table if not exists "articles" (
  `id` text not null primary key,
  `url` text not null,
  `title` text not null,
  `desc` text not null,
  `created_at` integer not null,
  `updated_at` integer not null
);
CREATE INDEX articles_created_at_idx ON articles (created_at);
'''

FEED_FILE = "data/gendai.xml"
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

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' \
             ' AppleWebKit/537.36 (KHTML, like Gecko)' \
             ' Chrome/80.0.3987.106 Safari/537.36'

BASE_URL = 'https://www.nikkan-gendai.com/'


DB_FILE = 'gendai.sqlite'
db = records.Database(f'sqlite:///./{DB_FILE}')

client = httpx.Client(headers={'User-Agent': USER_AGENT})


def format_time(epoch: int):
    return datetime.utcfromtimestamp(epoch).isoformat() + 'Z'


def parse_time(text: str):
    return int(parse_dt(text).timestamp())


def parse_id(url: str):
    i = url.rfind('/')
    return url[i+1:]


def crawl_article(href: str):
    url = f'{BASE_URL}{href}' if href.startswith('/') else href
    existing = db.query('select * from articles where url = :url', url=url, fetchall=True)
    if existing.all(): return
    r = client.get(url)
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
    db.query(
        '''
        insert into articles (`id`, `url`, `title`, `desc`, `created_at`, `updated_at`)
        values (:id, :url, :title, :desc, :created_at, :updated_at)
        on conflict (`id`) do update
            set `url` = :url,
                `title` = :title,
                `desc` = :desc,
                `updated_at` = :updated_at
        ''',
        id=id,
        url=url,
        title=title,
        desc=desc,
        created_at=created_at,
        updated_at=updated_at,
    )


def crawl_rss():
    r = client.get(BASE_URL)
    assert r.status_code == 200
    dom = lxml.html.fromstring(r.content)
    xs = dom.cssselect('a[href]')
    for x in xs:
        href = x.attrib['href']
        if '/articles/view/' not in href:
            continue
        crawl_article(href)
    pass


def write_rss():
    query = ''' select * from articles order by updated_at desc limit 30 '''
    items = [
        {
            'title': x.title,
            'url': x.url,
            'date': format_time(x.updated_at),
            'id': x.id,
            'desc': x.desc,
        }
        for x in db.query(query, fetchall=True)
    ]
    data = {
        'feed_url': config.FEED_URL,
        'feed_id': config.SANKEI_ID,
        'last_updated': format_time(int(time.time())),
        'items': items,
    }
    result = pystache.render(pystache.parse(TEMPLATE), context=data)
    with open(FEED_FILE, 'w') as f:
        f.write(result)


def main():
    crawl_rss()
    write_rss()


if __name__ == '__main__':
    main()
