from typing import NamedTuple
import hashlib


class MSql(NamedTuple):
    desc: str
    sql: str

    def sha256(self):
        assert self.sql.strip()
        h = hashlib.sha256()
        h.update(self.sql.encode('utf-8'))
        return h.hexdigest()


MIGRATIONS = [
    MSql('setup news_articles', '''
create table if not exists "news_articles" (
  "agency" text not null,
  "id" text not null,
  "url" text not null,
  "title" text not null,
  "desc" text null,
  "created_at" timestamptz not null default NOW(),
  "updated_at" timestamptz not null default NOW(),
  primary key (id, agency)
);
    '''),

    MSql('add index for news_articles', '''
create index news_articles_updated_at on news_articles (updated_at, agency, id);
create index news_articles_created_at on news_articles (created_at, agency, id);
    '''),

    MSql('index news_articles.url', '''
create index news_articles_url on news_articles (url);
    '''),

    MSql('create fav_tweets', '''
create table fav_tweets (
  "id" numeric not null primary key,
  "tweet" jsonb not null,
  "created_at" timestamptz not null
);
create index idx_fav_tweets_created_at on fav_tweets (created_at);
    '''),

    MSql('create timeline_tweets', '''
create table timeline_tweets (
  "id" numeric not null primary key,
  "tweet" jsonb not null,
  "created_at" timestamptz not null
);
create index idx_timeline_tweets_created_at on timeline_tweets (created_at);
    ''')
]
