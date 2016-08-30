#!/usr/bin/env python3
# vim: coding=utf-8:

# http://developer.qiniu.com/article/index.html

from __future__ import unicode_literals, division
import requests as _requests
import hmac
from hashlib import sha1
from base64 import urlsafe_b64encode
import logging
from path import Path
from urllib.parse import urlparse, urlencode
import os

# global pool
requests = _requests.session()


class Qiniu(object):
    RSF_HOST = 'rsf.qbox.me'
    RS_HOST = 'rs.qiniu.com'
    UP_HOST = 'upload.qiniu.com'

    def __init__(self, authkey):
        self.authkey = authkey

    def post(self, host, api_path, queries):
        encoded_query = urlencode({k: v for k, v in queries.items() if v is not None})
        if encoded_query != '':
            encoded_query = '?' + encoded_query
        url = 'https://{}{}{}'.format(host, api_path, encoded_query)
        signature = self.authkey.sign(api_path, encoded_query)
        return requests.post(url, headers={'Authorization': 'QBox {}'.format(signature)})

    def list(self, bucket, limit=None, prefix=None, delimiter=None, marker=None):
        queries = {
            'bucket': bucket,
            'limit': limit,
            'prefix': prefix,
            'delimiter': delimiter,
            'marker': marker
        }
        return self.post(self.RSF_HOST, '/list', queries)

    def list_all(self, bucket, prefix=None):
        items = []
        marker = None
        while True:
            r = self.list(bucket, marker=marker, prefix=prefix)
            assert r.ok
            result = r.json()
            if 'items' in result:
                items.extend(result['items'])

            if 'marker' in result:
                marker = result['marker']
            else:
                break
        return items


class AuthKey(object):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def sign(self, path, query='', body=''):
        signbody = '{}{}\n{}'.format(path, query, body)
        digest = hmac.new(self.secret.encode('utf-8'), signbody.encode('utf-8'), sha1).digest()
        return '{}:{}'.format(self.key, urlsafe_b64encode(digest).decode('utf-8'))


def current_auth_key():
    keyfile = Path(os.path.join(os.path.expanduser('~'), '.qiniu'))
    if keyfile.exists():
        import json
        with open(keyfile) as f:
            cont = json.loads(f.read())
            return AuthKey(cont['key'], cont['secret'])
    elif 'QINIU_KEY' in os.environ and 'QINIU_SECRET' in os.environ:
        return AuthKey(os.environ['QINIU_KEY'], os.environ['QINIU_SECRET'])
    else:
        raise RuntimeError("no key/secret exists (use `~/.qiniu` or env variable)")


def retry(max_retry=3):
    def _retry(f, *args, **kwargs):
        n = max_retry
        while n > 0:
            try:
                return f(*args, **kwargs)
            except:
                logging.exception("error executing " + f)
            n -= 1
    return _retry


def strip_left(orig, target):
    if orig.startswith(target):
        return orig[len(target)]
    raise RuntimeError("original string doesn't contain target: <{}>, <{}>".format(orig, target))


def joinpath(*args):
    agg = ''
    for seg in args:
        if agg == '':
            # first one, preserve `/` in the left
            agg += seg
        else:
            agg += '/'
            agg += seg.lstrip('/')
    return agg


class QiniuUtil(object):
    _HASH_BLOCK_SIZE = 1024 * 1024 * 4

    @staticmethod
    def _file_iter(input_stream, size, offset=0):
        """读取输入流:
        Args:
            input_stream: 待读取文件的二进制流
            size:         二进制流的大小
        Raises:
            IOError: 文件流读取失败
        """
        input_stream.seek(offset)
        d = input_stream.read(size)
        while d:
            yield d
            d = input_stream.read(size)

    @staticmethod
    def _sha1(data):
        """单块计算hash:
        Args:
            data: 待计算hash的数据
        Returns:
            输入数据计算的hash值
        """
        h = sha1()
        h.update(data)
        return h.digest()

    @staticmethod
    def etag_stream(input_stream):
        """计算输入流的etag:
        etag规格参考 http://developer.qiniu.com/docs/v6/api/overview/appendix.html#qiniu-etag
        Args:
            input_stream: 待计算etag的二进制流
        Returns:
            输入流的etag值
        """
        array = [QiniuUtil._sha1(block) for block in QiniuUtil._file_iter(input_stream, QiniuUtil._HASH_BLOCK_SIZE)]
        if len(array) == 0:
            array = [QiniuUtil._sha1(b'')]
        if len(array) == 1:
            data, = array
            prefix = b'\x16'
        else:
            sha1_str = b''.join(array)
            data = QiniuUtil._sha1(sha1_str)
            prefix = b'\x96'
        return urlsafe_b64encode(prefix + data)

    @staticmethod
    def etag(filePath):
        """计算文件的etag:
        Args:
            filePath: 待计算etag的文件路径
        Returns:
            输入文件的etag值
        """
        with open(filePath, 'rb') as f:
            return QiniuUtil.etag_stream(f).decode('utf-8')


class Storage(object):
    @staticmethod
    def new(auth, url):
        uri = urlparse(url)
        # ParseResult(scheme='', netloc='', path='', params='', query='', fragment='')
        if uri.scheme in ('qiniu', 'q', 'qn'):
            return QiniuStorage(auth, uri.netloc, uri.path)
        elif url.scheme in ('', 'file'):
            return LocalStorage(uri.netloc + uri.path)
        else:
            raise RuntimeError("Unknown path format: {}".format(url))

    pass


class LocalStorage(Storage):
    def __init__(self, basepath):
        self.basepath = basepath.rstrip('/')
        self.filelist = self.scan()
        self.fileobjects = [LocalObject(x, self.basepath) for x in self.filelist]
        self.files = {x.path(): x for x in self.fileobjects}

    def type(self):
        return 'local'

    def scan(self):
        p = Path(self.basepath)
        assert p.exists()
        if p.isdir():
            return list(self.walk_dir(str(p)))
        else:
            raise RuntimeError("path is not a directory: {}".format(self.basepath))

    def walk_dir(self, dirpath):
        for root, _, files in os.walk(dirpath):
            for path in files:
                yield strip_left(joinpath(root, path), dirpath).lstrip('/')


class QiniuStorage(Storage):
    def __init__(self, auth, bucket, basepath):
        self.auth = auth
        self.bucket = bucket
        self.baseprefix = basepath.lstrip('/')
        self.filelist = self.scan()
        self.fileobjects = [QiniuObject(x, self.baseprefix) for x in self.filelist]
        self.files = {x.path(): x for x in self.fileobjects}

    def type(self):
        return 'qiniu'

    def scan(self):
        qn = Qiniu(self.auth)
        return qn.list_all(self.bucket, prefix=self.baseprefix)


class FileObject(object):
    def path(self):
        pass

    def size(self):
        pass

    def qetag(self):
        pass


class LocalObject(FileObject):
    def __init__(self, path, basepath):
        self.relpath = path
        self.basepath = basepath

    def fullpath(self):
        return joinpath(self.basepath, self.relpath)

    def path(self):
        return self.relpath

    def size(self):
        return Path(self.fullpath()).size

    def qetag(self):
        return QiniuUtil.etag(self.fullpath())


class QiniuObject(FileObject):
    """
    {
      "key": "duplicity-full.20160817T150035Z.vol4.difftar.gpg",
      "hash": "lpNs_-6JIpe9qjdWA9L7Qc8r3pOK",
      "fsize": 209764896,
      "mimeType": "application/pgp-encrypted",
      "putTime": 14714478455502964
    }
    """
    def __init__(self, props, basepath):
        self.key = props['key']
        self.hash = props['hash']
        self.fsize = props['fsize']
        self.putTime = props['putTime']
        self.rel_path = strip_left(self.key, basepath).lstrip('/')

    def path(self):
        return self.rel_path

    def size(self):
        return self.fsize

    def qetag(self):
        return self.hash


class SyncUtil(object):
    @staticmethod
    def sync(src, dst):
        assert type(src) in (QiniuStorage, LocalStorage)\
               and type(dst) in (QiniuStorage, LocalStorage)\
               and type(dst) != type(src)
        srcpaths = set(src.files.keys())
        dstpaths = set(dst.files.keys())
        toupload = srcpaths.difference(dstpaths)
        toremove = dstpaths.difference(srcpaths)
        tooverride = SyncUtil.check_override(srcpaths.intersection(dstpaths), src, dst)

    @staticmethod
    def check_override(fileset, src, dst):
        def is_different(a, b):
            return a.size() == b.size() and a.qetag() == b.qetag()
        return [
            p for p in fileset
            if is_different(src.files[p], dst.files[p])
        ]


def main():
    import argparse
    parser = argparse.ArgumentParser(description='sync qiniu')
    parser.add_argument('source', type=str, help='local path or `<bucket>/optional/path`')
    parser.add_argument('target', type=str, help='same with source, one should be local path, the other should be remote url')
    parser.add_argument('-f', metavar='force', type=bool, default=False)
    parser.add_argument('-d', metavar='delete', type=bool, default=False)
    args = parser.parse_args()
    authkey = current_auth_key()
    src = Storage.new(authkey, args.source)
    dst = Storage.new(authkey, args.target)
    SyncUtil.sync(src, dst)
    print(args)


def main2():
    authkey = current_auth_key()
    qiniu = Qiniu(authkey)
    r = qiniu.list_all('tsu-repos')
    print(r)
    print(r.text)


if __name__ == '__main__':
    # main()
    main2()
