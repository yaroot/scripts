import requests
import records
import logging
import lxml

DB_FILE = 'sankei.sqlite'
db = records.Database(f'sqlite:///./{DB_FILE}')

SCHEMA = '''
create table if not exists "articles" (
    `url` text primary key,
    `title` text,
    `created_at` integer not null,
    `updated_at` integer not null
);
CREATE INDEX articles_created_at_idx ON articles (created_at);
'''

URL = 'https://www.sankei.com/flash/newslist/flash-n1.html'



