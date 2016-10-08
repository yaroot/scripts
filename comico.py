#!/usr/bin/env python3

from urllib.parse import urlparse, parse_qs
from os import mkdir
from os.path import basename, join as pathjoin, exists as pathexists, isdir
import re
import requests

httpsession = requests.session()
httpsession.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.34 Safari/537.36'


def parse_url_for_title_and_episode(url):
    # ParseResult(scheme='http', netloc='www.comico.com.tw', path='/detail.nhn',
    #   params='', query='titleNo=1&articleNo=1', fragment='')
    # {'articleNo': ['1'], 'titleNo': ['1']}
    res = urlparse(url)
    query = parse_qs(res.query)
    return query['titleNo'][0], query['articleNo'][0]


def parse_image_url(url):
    r = httpsession.get(url, headers={'Referer': url})
    assert r.ok
    if '//www.comico.jp' in url:
        # jp
        return [
            i
            for l in r.text.splitlines()
            if 'primaryImageOfPage' in l
            for i in re.findall('src="([^"]+)"', l)
        ]
    elif '//www.comico.com.tw' in url:
        return [
            i
            for l in r.text.splitlines()
            if '_image' in l
            for i in re.findall('src="([^"]+)"', l)
            ]
    elif '//www.cncomico.com' in url:
        return [
            i
            for l in r.text.splitlines()
            if '/comicimg.' in l
            for i in re.findall('src="([^"]+)"', l)
        ]
    else:
        print('could not found any comic images')
        return []


def download_into(target_dir, img_url, referer_url):
    print('%s ==> %s' % (target_dir, img_url))
    img_name = basename(img_url)
    assert len(img_name) > 0
    r = httpsession.get(img_url, headers={'Referer': referer_url})
    assert r.ok
    assert 'image/' in r.headers['Content-Type']
    fullpath = pathjoin(target_dir, img_name)
    print('saving size <%d> to %s' % (len(r.content), fullpath))
    with open(fullpath, 'wb') as f:
        f.write(r.content)


def parse_and_download(url):
    if 'comico.' not in url:
        print('url is not comico.jp or comico.com.tw')
        return
    titleNo, articleNo = parse_url_for_title_and_episode(url)
    target_dir = '%s-%s' % (titleNo, articleNo)
    print('creating directory: %s' % target_dir)
    if not pathexists(target_dir):
        mkdir(target_dir)
    assert isdir(target_dir)
    image_urls = parse_image_url(url)
    for img_url in image_urls:
        download_into(target_dir, img_url, url)

def main(argv):
    for url in argv[1:]:
        print('parsing %s' % url)
        parse_and_download(url)

if __name__ == '__main__':
    main(__import__('sys').argv)
