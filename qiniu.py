#!/usr/bin/env python3
# coding=utf-8

# http://developer.qiniu.com/article/index.html

from __future__ import unicode_literals, division
import hmac
from hashlib import sha1
from base64 import urlsafe_b64encode
import logging as _logger_factory
from pathlib import Path
from urllib.parse import urlparse, urlencode
import os
from datetime import datetime, timedelta
import json
from time import sleep
import requests as _requests_factory
import progressbar

logger = _logger_factory.getLogger(__name__)

# global pool
requests = _requests_factory.session()


class Qiniu(object):
    RSF_HOST = 'rsf.qbox.me'
    RS_HOST = 'rs.qbox.me'
    UP_HOST = 'up.qbox.me'

    def __init__(self, authkey):
        self.authkey = authkey

    def generate_upload_token(self, bucket, target_path):
        put_policy = {
            'scope': '{}:{}'.format(bucket, target_path),
            'deadline': int((datetime.now() + timedelta(days=1)).timestamp()),
        }
        upload_token = self.authkey.sign_upload_policy(json.dumps(put_policy))
        return upload_token

    def post(self, host, api_path, queries=None):
        if queries is None:
            queries = {}
        encoded_query = urlencode({k: v for k, v in queries.items() if v is not None})
        if encoded_query != '':
            encoded_query = '?' + encoded_query
        url = 'https://{}{}{}'.format(host, api_path, encoded_query)
        signature = self.authkey.sign_request(api_path, encoded_query)
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
            assert_response(r)
            result = r.json()
            if 'items' in result:
                items.extend(result['items'])

            if 'marker' in result:
                marker = result['marker']
            else:
                break
        return items

    def upload(self, local_path, bucket, target_path):
        if file_size(local_path) > QiniuUtil.BLOCK_SIZE:
            self.upload_multiblock(local_path, bucket, target_path)
        else:
            self.upload_singleshot(local_path, bucket, target_path)

    def upload_singleshot(self, local_path, bucket, target_path):
        logger.debug('uploading <{}> to <{}:{}>'.format(local_path, bucket, target_path))
        upload_token = self.generate_upload_token(bucket, target_path)
        with open(local_path, 'rb') as f:
            r = requests.post('https://{}/'.format(self.UP_HOST), files={
                'key': ('', target_path),
                'token': ('', upload_token),
                'file': ('', f),
            })
        assert_response(r)

    def upload_multiblock(self, local_path, bucket, target_path):
        logger.debug('uploading multiblock <{}> to <{}:{}>'.format(local_path, bucket, target_path))
        total_size = file_size(local_path)
        upload_token = self.generate_upload_token(bucket, target_path)
        pbar = PBarUtil.new(total_size).start()  # will not be accurate during retries
        with open(local_path, 'rb') as f:
            ctxes = [
                retry(max_retry=3, func=lambda: self.upload_block(pbar, blk, upload_token))
                for blk in QiniuUtil.iter_file(f)]
        pbar.finish()
        return retry(max_retry=3, func=lambda: self.upload_mkfile(total_size, ctxes, upload_token, bucket, target_path))

    # mkblk response
    # {
    #     "ctx":          "<Ctx           string>",
    #     "checksum":     "<Checksum      string>",
    #     "crc32":         <Crc32         int64>,
    #     "offset":        <Offset        int64>,
    #     "host":         "<UpHost        string>"
    # }
    def upload_block(self, pbar, blk, upload_token):
        blk_size = len(blk)
        logger.debug('uploading block, size {}'.format(blk_size))

        def blk_gen():
            chunk_size = 128 * 1024  # 32k
            chunks = (blk[i:i+chunk_size] for i in range(0, blk_size, chunk_size))
            for chunk in chunks:
                pbar.update(min(pbar.currval + len(chunk), pbar.maxval))
                yield chunk

        r = requests.post(
            'https://{}/mkblk/{}'.format(self.UP_HOST, blk_size),
            data=blk_gen(),
            headers={
                'Content-Type': 'application/octet-stream',
                'Authorization': 'UpToken {}'.format(upload_token)
            }
        )

        assert_response(r)
        return r.json()['ctx']

    def upload_mkfile(self, file_size, ctxes, upload_token, bucket, target_path):
        logger.debug('finishing multi block upload, creating file from {}'.format(','.join(ctxes)))
        encoded_scope = urlsafe_b64encode(target_path.encode('utf-8')).decode('utf-8')
        r = requests.post(
            'https://{}/mkfile/{}/key/{}'.format(self.UP_HOST, file_size, encoded_scope),
            data=','.join(ctxes).encode('utf-8'),
            headers={
                'Content-Type': 'text/plain',
                'Authorization': 'UpToken {}'.format(upload_token)
            }
        )
        assert_response(r)
        pass

    def download(self, bucket, target_path, local_path):
        pass

    def delete(self, bucket, target_path):
        logger.debug('delete <{}:{}>'.format(bucket, target_path))
        entry_uri = urlsafe_b64encode('{}:{}'.format(bucket, target_path).encode('utf-8')).decode('utf-8')
        r = self.post(self.RS_HOST, '/delete/{}'.format(entry_uri))
        assert_response(r)


class AuthKey(object):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def hmac_sha1(self, content):
        # content has to be bytes
        digest = hmac.new(self.secret.encode('utf-8'), content, sha1).digest()
        return urlsafe_b64encode(digest).decode('utf-8')

    def sign_request(self, path, query='', body=''):
        signbody = '{}{}\n{}'.format(path, query, body)
        sign = self.hmac_sha1(signbody.encode('utf-8'))
        return '{}:{}'.format(self.key, sign)

    def sign_upload_policy(self, policy):
        encodedPolicy = urlsafe_b64encode(policy.encode('utf-8'))
        sign = self.hmac_sha1(encodedPolicy)
        return '{}:{}:{}'.format(self.key, sign, encodedPolicy.decode('utf-8'))


def current_auth_key():
    keyfile = Path(os.path.join(os.path.expanduser('~'), '.qiniu_access'))
    if keyfile.exists():
        with keyfile.open() as f:
            cont = json.loads(f.read())
            return AuthKey(cont['key'], cont['secret'])
    elif 'QINIU_KEY' in os.environ and 'QINIU_SECRET' in os.environ:
        return AuthKey(os.environ['QINIU_KEY'], os.environ['QINIU_SECRET'])
    else:
        raise RuntimeError("no key/secret exists (use `~/.qiniu_access` or env variable)")


def retry(func, max_retry=3):
    n = max_retry
    while n > 0:
        try:
            return func()
        except:
            logger.exception("error executing {}".format(func))
            n -= 1
        sleep(0.05)
    raise RuntimeError('max_retry reached, {} failed'.format(func))


def strip_left(orig, target):
    if orig.startswith(target):
        return orig[len(target):].lstrip('/')
    raise RuntimeError("original string doesn't contain target: <{}>, <{}>".format(orig, target))


def joinpath(*args):
    agg = ''
    for seg in args:
        if agg == '':
            # first one, preserve `/` on the left
            agg += seg
        else:
            agg = '{}/{}'.format(agg.rstrip('/'), seg.lstrip('/'))
    return agg


def info(stuff):
    print(stuff)


def assert_response(r):
    if not r.ok:
        raise RuntimeError('request failed {} detail: {}'.format(r.status_code, r.text))


def file_size(path):
    return Path(path).stat().st_size


class PBarUtil(object):
    @staticmethod
    def new(maxval):
        pbar = progressbar.ProgressBar(
            maxval=maxval,
            term_width=80,
            poll=0.1,
            left_justify=False,
            widgets=[
                progressbar.Bar(), ' ',
                progressbar.Percentage(), ' ',
                progressbar.FileTransferSpeed(), ' ',
                progressbar.ETA(), ' ',
            ]
        )
        return pbar


class QiniuUtil(object):
    BLOCK_SIZE = 1024 * 1024 * 4

    @staticmethod
    def iter_file(input_stream, size=BLOCK_SIZE, offset=0):
        input_stream.seek(offset)
        d = input_stream.read(size)
        while d:
            yield d
            d = input_stream.read(size)

    @staticmethod
    def _sha1(data):
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
        array = [QiniuUtil._sha1(block) for block in QiniuUtil.iter_file(input_stream)]
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
    def etag(file_path):
        """计算文件的etag:
        Args:
            file_path: 待计算etag的文件路径
        Returns:
            输入文件的etag值
        """
        logger.debug('hashing {}'.format(file_path))
        with open(file_path, 'rb') as f:
            return QiniuUtil.etag_stream(f).decode('utf-8')


class Storage(object):
    @staticmethod
    def new(auth, url):
        uri = urlparse(url)
        # ParseResult(scheme='', netloc='', path='', params='', query='', fragment='')
        if uri.scheme in ('qiniu', 'q', 'qn'):
            return QiniuStorage(auth, uri.netloc, uri.path)
        elif uri.scheme in ('', 'file'):
            return LocalStorage(uri.netloc + uri.path)
        else:
            raise RuntimeError("Unknown path format: {}".format(url))

    def type(self): pass

    def upload(self, fileobject): pass

    def delete(self, fileobject): pass

    pass


class LocalStorage(Storage):
    def __init__(self, basepath):
        self.basepath = os.path.expanduser(basepath).rstrip('/')
        self.filelist = self.scan()
        self.fileobjects = [LocalObject(x, self.basepath) for x in self.filelist]
        self.files = {x.path(): x for x in self.fileobjects}

    def type(self):
        return 'local'

    def scan(self):
        p = Path(self.basepath)
        assert p.exists()
        if p.is_dir():
            return list(self.walk_dir(str(p)))
        else:
            raise RuntimeError("path is not a directory: {}".format(self.basepath))

    def walk_dir(self, dirpath):
        for root, _, files in os.walk(dirpath):
            for path in files:
                yield strip_left(joinpath(root, path), dirpath)


class QiniuStorage(Storage):
    def __init__(self, auth, bucket, basepath):
        self.auth = auth
        self.qiniu = Qiniu(auth)
        self.bucket = bucket
        self.baseprefix = basepath.lstrip('/')
        self.filelist = self.scan()
        self.fileobjects = [QiniuObject(x, self.baseprefix) for x in self.filelist]
        self.files = {x.path(): x for x in self.fileobjects}

    def type(self):
        return 'qiniu'

    def scan(self):
        return self.qiniu.list_all(self.bucket, prefix=self.baseprefix)

    def upload(self, fileobject):
        assert type(fileobject) == LocalObject
        localpath = fileobject.fullpath()
        remotepath = joinpath(self.baseprefix, fileobject.path())
        self.qiniu.upload(localpath, self.bucket, remotepath)

    def delete(self, fileobject):
        assert type(fileobject) == QiniuObject
        remotepath = joinpath(self.baseprefix, fileobject.path())
        self.qiniu.delete(self.bucket, remotepath)


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
        return file_size(self.fullpath())

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
        self.rel_path = strip_left(self.key, basepath)

    def path(self):
        return self.rel_path

    def size(self):
        return self.fsize

    def qetag(self):
        return self.hash


class SyncUtil(object):
    @staticmethod
    def sync(args, src, dst):
        assert type(src) in (QiniuStorage, LocalStorage)\
               and type(dst) in (QiniuStorage, LocalStorage)\
               and type(dst) != type(src)
        srcpaths = set(src.files.keys())
        dstpaths = set(dst.files.keys())
        toupload = srcpaths.difference(dstpaths)
        toremove = dstpaths.difference(srcpaths)
        tooverride = SyncUtil.check_override(srcpaths.intersection(dstpaths), src, dst, args.skip_etag)
        SyncUtil.do_upload(args, src, dst, [src.files[x] for x in toupload])
        SyncUtil.do_override(args, src, dst, [src.files[x] for x in tooverride])
        SyncUtil.do_delete(args, src, dst, [dst.files[x] for x in toremove])

    @staticmethod
    def do_delete(args, src, dst, todelete):
        for fo in todelete:
            info('delete <{}>'.format(fo.path()))
            if args.force and args.delete:
                dst.delete(fo)

    @staticmethod
    def do_upload(args, src, dst, toupload):
        for fo in toupload:
            info('upload <{}>'.format(fo.path()))
            if args.force:
                dst.upload(fo)

    @staticmethod
    def do_override(args, src, dst, tooverride):
        for fo in tooverride:
            info('override <{}>'.format(fo.path()))
            if args.force and args.delete:
                dst.upload(fo)

    @staticmethod
    def check_override(fileset, src, dst, skip_etag):
        def is_same(a, b):
            return a.size() == b.size() and (skip_etag or a.qetag() == b.qetag())
        return [
            p for p in fileset
            if not is_same(src.files[p], dst.files[p])
        ]


def main():
    import argparse
    parser = argparse.ArgumentParser(description='sync qiniu')
    parser.add_argument('source', type=str, help='local path or `<bucket>/optional/path`')
    parser.add_argument('target', type=str, help='same with source, one should be local path, the other should be remote url')
    parser.add_argument('--force', '-f', action='store_true', default=False)
    parser.add_argument('--delete', '-d', action='store_true', default=False)
    parser.add_argument('--verbose', '-v', action='store_true', default=False)
    parser.add_argument('--skip-etag', '-s', action='store_true', default=False)
    args = parser.parse_args()

    _logger_factory.basicConfig(
        level=args.verbose and _logger_factory.DEBUG or _logger_factory.WARN,
        format='%(levelname)-5s %(asctime)s %(name)s %(message)s'
    )

    authkey = current_auth_key()
    src = Storage.new(authkey, args.source)
    dst = Storage.new(authkey, args.target)
    SyncUtil.sync(args, src, dst)


if __name__ == '__main__':
    main()
