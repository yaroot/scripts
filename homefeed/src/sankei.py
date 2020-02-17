import httpx
import records
import logging
import time
from datetime import datetime, timedelta, timezone
import pystache
from . import config

DB_FILE = 'sankei.sqlite'
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

FEED_FILE = "data/sankei.json"
TEMPLATE = """
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>産経新聞</title>
    <link href="{{ feed_url }}/sankei.json" rel="self" />
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

URL = 'https://www.sankei.com/json/newslist/flash.json'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' \
             ' AppleWebKit/537.36 (KHTML, like Gecko)' \
             ' Chrome/80.0.3987.106 Safari/537.36'


def format_time(epoch: int):
    return datetime.utcfromtimestamp(epoch).isoformat() + 'Z'


def parse_date(text):
    d = datetime.strptime(text, '%Y/%m/%d %H:%M:%S') - timedelta(hours=9)
    d = d.replace(tzinfo=timezone.utc)
    return int(d.timestamp())


def crawl_new():
    r = httpx.get(URL, headers={'user-agent': USER_AGENT})
    assert not r.is_error
    articles = r.json()['article']
    for art in articles:
        _id = art['id']
        date = art['date']
        title = art['title']
        url = art['url']
        genre = art['parent_genre_name']
        date = parse_date(date)

        db.query(
            ''' insert into articles (`id`, `url`, `title`, `created_at`, `updated_at`)
                values (:id, :url, :title, :created_at, :updated_at)
                on conflict (`id`) do update
                    set `url` = :url,
                        `title` = :title,
                        `updated_at` = :updated_at
            ''',
            id=_id,
            title='%s: %s' % (genre, title),
            url=url,
            created_at=date,
            updated_at=date,
        )


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
        'feed_id': config.SANKEI_ID,
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
