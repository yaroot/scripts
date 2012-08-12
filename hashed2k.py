#!/usr/bin/env python
# coding=utf-8

import hashlib

# https://www.radicand.org/edonkey2000-hash-in-python/
def hash_file(file_path):
    """ Returns the ed2k hash of a given file. 

        credit: https://www.radicand.org/edonkey2000-hash-in-python/
    """

    md4 = hashlib.new('md4').copy

    def gen(f):
        while True:
            x = f.read(9728000)
            if x: yield x
            else: return

    def md4_hash(data):
        m = md4()
        m.update(data)
        return m

    with open(file_path, 'rb') as f:
        a = gen(f)
        hashes = [md4_hash(data).digest() for data in a]
        if len(hashes) == 1:
            return hashes[0].encode("hex")
        else:
            return md4_hash(reduce(lambda a,d: a + d, hashes, "")).hexdigest()


if __name__ == '__main__':
    import sys
    from os.path import basename, getsize

    filename = sys.argv[1]

    sys.stdout.write(u'ed2k://|file|%s|%d|%s|/\n' % (basename(filename),
            getsize(filename),
            hash_file(filename)
            ))

