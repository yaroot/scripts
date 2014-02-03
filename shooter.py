#!/usr/bin/env python2
# credit: http://code.google.com/p/sevenever/source/browse/trunk/misc/fetchsub.py

from __future__ import unicode_literals

import argparse
import hashlib
import sys
import os
import requests


def hash_block(f, offset):
    f.seek(offset)
    b = f.read(4096)
    return hashlib.md5(b).hexdigest()


def hash_file(f, fsize):
    if fsize < 8192:
        return None

    offsets = [
        4096,
        fsize / 3 * 2,
        fsize / 3,
        fsize - 8192
    ]

    hashes = [ hash_block(f, offset) for offset in offsets ]
    return ';'.join(hashes)


def query_shooter(fhash, fname):
    query_data = {
        'filehash': fhash,
        'pathinfo': fname,
        'format': 'json',
    }
    resp = requests.post('http://shooter.cn/api/subapi.php', data=query_data)

    if resp.ok:
        try:
            return resp.json()
        except:
            pass
    return None


def request_subtitle(link):
    r = requests.get(link, verify=False) # RapidSSL, so...
    if r.ok:
        return r.content
    return None


def gen_subtitle_fname(fname, ext):
    i = fname.rfind('.')
    if i < 1:
        return None
    name = fname[:i]
    return '%s.%s' % (name, ext)


def download_sub_file(subs, fname):
    for sub in subs:
        ext = sub['Ext']
        link = sub['Link']

        subcontent = request_subtitle(link)
        subfname = gen_subtitle_fname(fname, ext)
        if subfname is None or subcontent is None:
            print 'Not be able to download subtitles for: %s' % fname
        with open(subfname, 'wb') as f:
            print 'Writing: %s' % subfname
            f.write(subcontent)



def download_subtitle(f):
    fpath = f.name
    fname = os.path.basename(fpath)
    fd = f.fileno()
    fsize = os.lseek(f.fileno(), 0, os.SEEK_END)
    fhash = hash_file(f, fsize)
    if fhash is None:
        print 'Not be able to download subtitles for: %s' % fname
        return

    subs = query_shooter(fhash, fname)

    if len(subs) == 0:
        print 'Not be able to download subtitles for: %s' % fname
        return

    download_sub_file(subs[0]['Files'], fname)



if __name__ == '__main__':
    parser = argparse.ArgumentParser('download subtitles from shooter')
    parser.add_argument('video_files', metavar='file', type=file, nargs='+')

    args = parser.parse_args()
    for f in args.video_files:
        download_subtitle(f)

