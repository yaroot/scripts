from typing import Iterator
import os
import sys

import minio
from minio.datatypes import Object, Bucket
from minio.commonconfig import CopySource

cli = minio.Minio(
    endpoint=os.environ['ENDPOINT'],
    access_key=os.environ['ACCESS_KEY'],
    secret_key=os.environ['SECRET_KEY'],
)


def iter_objects(bucket, prefix) -> Iterator[Object]:
    for x in cli.list_objects(bucket, prefix=prefix):
        x: Object = x
        if x.is_dir:
            yield from iter_objects(bucket, x.object_name)
        else:
            yield x
    pass


def list(bucket, prefix=None):
    for x in iter_objects(bucket, prefix):
        print('- %s %d %s' % (x.object_name, x.size, x.last_modified))


def list_bucket():
    for b in cli.list_buckets():
        b: Bucket = b
        print('%18s  %s' % (b.name, b.creation_date))
    pass


def set_cache(maxage, bucket, prefix):
    cache_header = 'Cache-Control'
    cache_value = f'public,max-age={maxage}'
    for x in iter_objects(bucket, prefix):
        stat: Object = cli.stat_object(bucket, x.object_name)
        if stat.metadata.get(cache_header) != cache_value:
            print('set -> %15s' % stat.object_name)
            cli.copy_object(
                bucket_name=bucket,
                object_name=x.object_name,
                source=CopySource(bucket, x.object_name),
                metadata={cache_value: cache_value},
                metadata_directive='REPLACE',
            )
        pass
    pass


def main():
    act = sys.argv[1]
    args = sys.argv[2:]
    if act == 'lsb':
        list_bucket()
    elif act == 'ls':
        bucket = args[0]
        prefix = args[1] if args[1:] else None
        list(bucket, prefix)
    elif act == 'set-cache':
        maxage = int(args[0])
        bucket = args[1]
        prefix = args[2] if args[2:] else None
        set_cache(maxage, bucket, prefix)
    pass


if __name__ == '__main__':
    main()