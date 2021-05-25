#!/usr/bin/env python
# encoding=utf-8

import sys
from os.path import basename, getsize
import hashlib

# https://www.radicand.org/edonkey2000-hash-in-python/
def hash_file(file_path):
    """ Returns the ed2k hash of a given file.

        credit: https://www.radicand.org/edonkey2000-hash-in-python/
    """

    md4 = hashlib.new('md4').copy

    def iter(f):
        while True:
            x = f.read(9728000)
            if x: yield x
            else: return

    def md4_hash(data):
        m = md4()
        m.update(data)
        return m

    with open(file_path, 'rb') as f:
        hashes = [md4_hash(data).digest() for data in iter(f)]
        if len(hashes) == 1:
            return hashes[0].hex()
        else:
            return md4_hash(reduce(lambda a,d: a + d, hashes)).hexdigest()


def gen_ed2k_url(filename):
    _hash = hash_file(filename)
    link = 'ed2k://|file|%s|%d|%s|/' % (
        basename(filename),
        getsize(filename),
        _hash
    )
    return link


if __name__ == '__main__':
    for f in sys.argv[1:]:
        print(gen_ed2k_url(f))

