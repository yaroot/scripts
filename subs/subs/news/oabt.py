from typing import List
from datetime import datetime, timedelta
import logging
import lxml.html
import lxml.etree
import hashlib
import pytz
import time
from collections import namedtuple
from subs import services, config


URL = 'http://www.oabt007.com/index/index?c=yyets'

Piece = namedtuple('Piece', 'name size dt url')

TEMPLATE = """
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>oabt</title>
    <link href="{{ feed_url }}/oabt.xml" rel="self" />
    <link href="{{ feed_url }}" />
    <updated>{{ last_updated }}</updated>
    <id>urn:feed:{{ feed_id }}</id>

    {{ #items }}
    <entry>
        <title><![CDATA[{{ title }}]]></title>
        <link href="{{ url }}" />
        <updated>{{ date }}</updated>
        <id>{{ id }}</id>
        <content type="html"><![CDATA[{{& desc }}]]></content>
    </entry>
    {{ /items }}
</feed>
""".strip()


def parse_date(s):
    # '今天 2020-05-23'
    _, x = s.split(' ')
    y, m, d = map(int, x.split('-'))
    return datetime(y, m, d, tzinfo=pytz.utc) - timedelta(hours=8)


def parse_time(d: datetime, s):
    # '13:55
    h, m = map(int, s.split(':'))
    return d.replace(hour=h, minute=m)


def parse_day_list(d: datetime, p):
    for li in p.getchildren():
        name = li.cssselect('span.name')[0].text
        size = li.cssselect('span.size')[0].text
        clock = li.cssselect('span.time')[0].text
        url = li.cssselect('a.cp_magnet')[0].attrib['data-magnet']
        dt = parse_time(d, clock)
        yield Piece(name, size, dt, url)
    pass


def list_files():
    r = services.httpclient.get(URL)
    assert not r.is_error
    dom = lxml.html.fromstring(r.text)
    wrapper = dom.cssselect('div.link-list-wrapper')[0]
    _date = None
    pieces = []
    for p in wrapper.getchildren():
        tag = p.tag
        kls = list(p.classes)
        if tag == 'p' and 'link-list-title' in kls:
            _date = parse_date(p.text.strip())
        elif tag == 'ul' and 'link-list' in kls:
            assert _date is not None
            for x in parse_day_list(_date, p):
                pieces.append(x)
    return pieces


def write_rss(pieces: List[Piece]):
    items = [
        {
            'title': f'{p.name} ({p.size})',
            'url': 'http://www.oabt007.com',
            'date': services.format_ts(p.dt),
            'id': hash_name(p.name),
            'desc': f'''
                <a href='{p.url}'>{p.name}</a>
            ''',
        }
        for p in pieces
    ]
    data = {
        'feed_url': config.FEED_URL,
        'feed_id': config.GENDAI_ID,
        'last_updated': services.format_ts(int(time.time())),
        'items': items,
    }
    logging.info('Writing %d feeds (%s)', len(items), 'oabt')
    services.render_pystache_to(TEMPLATE, data, 'oabt.xml')


def hash_name(s: str):
    h = hashlib.sha256()
    h.update(s.encode('utf-8'))
    return h.hexdigest().lower()


def main():
    pieces = list_files()
    write_rss(pieces)
