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


# def gen_subtitle_fname(fname, ext):
#     i = fname.rfind('.')
#     if i < 1:
#         return None
#     name = fname[:i]
#     return '%s.%s' % (name, ext)


def download_sub_file(subs, fname):
    for sub in subs:
        ext = sub['Ext']
        link = sub['Link']

        subcontent = request_subtitle(link)
        subfname = '%s.%s' % (fname, ext) # gen_subtitle_fname(fname, ext)
        if subfname is None or subcontent is None:
            print 'Not be able to download subtitles for: %s' % fname
            return
        with open(subfname, 'wb') as f:
            print 'Writing: %s' % subfname
            f.write(subcontent)



def download_subtitle(f, list_only=False, file_no=None):
    fpath = f.name
    fname = os.path.basename(fpath).decode('utf-8')
    fd = f.fileno()
    fsize = os.lseek(f.fileno(), 0, os.SEEK_END)
    fhash = hash_file(f, fsize)
    if fhash is None:
        print 'Not be able to download subtitles for: %s' % fname
        return

    subs = query_shooter(fhash, fname)

    if subs is None or len(subs) == 0:
        print 'Not be able to download subtitles for: %s' % fname
        return

    if list_only:
        print '>', fname
        for i, sub in enumerate(subs, 1):
            exts = [s['Ext'] for s in sub['Files']]
            print i, ','.join(exts), '(delay %d)' % sub['Delay']
    else:
        if file_no is None:
            file_no = 1
        download_sub_file(subs[file_no - 1]['Files'], fname)



if __name__ == '__main__':
    parser = argparse.ArgumentParser('download subtitles from shooter')
    parser.add_argument('--list', '-l', action='store_true', help='list available subs')
    parser.add_argument('--file', '-f', type=int, dest='file_no', help='choose which sub to download')
    parser.add_argument('video_files', metavar='file', type=file, nargs='+', help='video files')

    args = parser.parse_args()

    for f in args.video_files:
        download_subtitle(f, args.list, args.file_no)

