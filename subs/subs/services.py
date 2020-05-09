from typing import Optional
import os.path
import httpx
from subs import db, config
from datetime import datetime, timezone
import pystache


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' \
             ' AppleWebKit/537.36 (KHTML, like Gecko)' \
             ' Chrome/80.0.3987.106 Safari/537.36'

httpclient = httpx.Client(headers={'User-Agent': USER_AGENT})


def upsert_news(
        agency: str,
        id: str,
        url: str,
        title: str,
        desc: Optional[str],
        created_at: int,
        updated_at: int
):
    with db.transaction():
        db.query(
            ''' insert into news_articles (agency, id, url, title, "desc", created_at, updated_at)
                values (:agency, :id, :url, :title, :desc,
                        to_timestamp(:created_at), to_timestamp(:updated_at))
                on conflict (id, agency) do update
                    set updated_at = to_timestamp(:updated_at)
                       ,url = :url
                       ,title = :title
                       ,"desc" = :desc
            ''',
            agency=agency,
            id=id,
            url=url,
            title=title,
            desc=desc,
            created_at=created_at,
            updated_at=updated_at,
        )
    pass


def recent_news(agency: str, size: int=50):
    with db.transaction():
        return db.query(
            'select * from news_articles where agency = :agency'
            ' order by updated_at desc'
            ' limit :limit',
            agency=agency,
            limit=size,
        ).all()
    pass


def news_by_url(agency: str, url: str):
    with db.transaction():
        return db.query(
            'select * from news_articles where url = :url and agency = :agency',
            url=url,
            agency=agency,
        ).all()
    pass


def format_ts(x):
    if type(x) in (int, float):
        x = datetime.utcfromtimestamp(x).replace(tzinfo=timezone.utc)
    assert type(x) == datetime
    assert x.tzinfo is not None
    return x.isoformat() + 'Z'


def render_pystache_to(template, context, filename):
    result = pystache.render(pystache.parse(template), context=context)
    path = os.path.join(config.PUB_DIR, filename)
    with open(path, 'w') as f:
        f.write(result)
    pass
