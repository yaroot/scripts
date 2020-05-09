import logging
from subs import db, migrations


INIT_MIGRATION = '''
create table if not exists migration_history (
    id int not null,
    "desc" text not null,
    created_at timestamptz not null,
    "sql" text not null,
    "sha256" text not null,
    constraint migration_history_pk primary key (id)
);
'''


def init_migration():
    with db.transaction():
        db.query(INIT_MIGRATION)
    pass


def query_history():
    with db.transaction():
        return db.query('select * from migration_history order by created_at').all()


def run_migration(index, m: migrations.MSql):
    with db.transaction():
        db.query(
            ''' insert into migration_history (id, "desc", created_at, sql, sha256)
                values (:id, :desc, now(), :sql, :sha256) ''',
            id=index,
            desc=m.desc,
            sql=m.sql,
            sha256=m.sha256(),
        )
        db.query(m.sql)
    pass


def run(dry_run: bool):
    init_migration()
    hist = query_history()
    hist = {
        r.id: r
        for r in hist
    }
    for i, m in enumerate(migrations.MIGRATIONS):
        if i in hist:
            r = hist[i]
            assert r.sha256 == m.sha256(), '''Migration %d checksum doesn't match (%s)''' % m.desc
            logging.info('Skip %d "%s" [%s]', i, m.desc, m.sha256())
        else:
            logging.info('Migrate %d "%s" [%s]', i, m.desc, m.sha256())
            if not dry_run:
                run_migration(i, m)
    pass
