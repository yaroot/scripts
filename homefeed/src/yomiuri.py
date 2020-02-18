import lxml.html
import lxml.etree
import httpx
import records
import logging
import time
from datetime import datetime, timedelta, timezone
import pystache
from . import config
from urllib.parse import urlparse

DB_FILE = 'yomiuri.sqlite'
db = records.Database(f'sqlite:///./{DB_FILE}')

SCHEMA = '''
create table if not exists "articles" (
  `id` text not null primary key,
  `url` text not null,
  `title` text not null,
  `created_at` integer not null,
  `updated_at` integer not null
);
CREATE INDEX articles_created_at_idx ON articles (created_at);
'''

FEED_FILE = "data/yomiuri.xml"
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

URL = 'https://www.yomiuri.co.jp/news/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' \
             ' AppleWebKit/537.36 (KHTML, like Gecko)' \
             ' Chrome/80.0.3987.106 Safari/537.36'


def format_time(epoch: int):
    return datetime.utcfromtimestamp(epoch).isoformat() + 'Z'


def capitalize(x: str):
    "local -> Local"
    return x[0].upper() + x[1:]


def crawl_new():
    r = httpx.get(URL, headers={'user-agent': USER_AGENT})
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

        db.query(
            ''' insert into articles (`id`, `url`, `title`, `created_at`, `updated_at`)
                values (:id, :url, :title, :created_at, :updated_at)
                on conflict (`id`) do update
                    set `url` = :url,
                        `title` = :title,
                        `updated_at` = :updated_at
            ''',
            id=_id,
            title=title,
            url=url,
            created_at=publish_time,
            updated_at=publish_time,
        )
    pass


def write_rss():
    query = ''' select * from articles order by updated_at desc limit 30 '''
    items = [
        {
            'title': x.title,
            'url': x.url,
            'date': format_time(x.updated_at),
            'id': x.id,
        }
        for x in db.query(query, fetchall=True)
    ]
    data = {
        'feed_url': config.FEED_URL,
        'feed_id': config.YOMIURI_ID,
        'last_updated': format_time(int(time.time())),
        'items': items,
    }
    result = pystache.render(pystache.parse(TEMPLATE), context=data)
    with open(FEED_FILE, 'w') as f:
        f.write(result)


def main():
    crawl_new()
    write_rss()


if __name__ == '__main__':
    main()
