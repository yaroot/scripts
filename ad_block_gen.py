#!/usr/bin/env python3
"""
lists source:
    https://firebog.net/
    https://github.com/StevenBlack/hosts



"""
from typing import Optional, List

import time
import ipaddress
from urllib.request import urlopen, Request
import os.path
import re

source_lists = [
    ('https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts', '# Start StevenBlack'),
    ('https://mirror1.malwaredomains.com/files/justdomains', ),
    ('http://sysctl.org/cameleon/hosts',),
    ('https://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt',),
    ('https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt',),

    # japan
    ('https://warui.intaa.net/adhosts/hosts.txt',),
    ('https://sites.google.com/site/hosts2ch/ja',),
    ('https://logroid.github.io/adaway-hosts/hosts_no_white.txt',),
    ('https://280blocker.net/files/280blocker_domain.txt',),

    # china
    ('https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-domains.txt',),
]

whitelist_domains = (
    'a248.e.akamai.net',
    's.yimg.jp',
    'c.kakaku.com',
    'lh3.googleusercontent.com',
    'yt3.ggpht.com',
    'lh3.ggpht.com',

    's3.amazonaws.com',
    'clients2.google.com',
    'clients3.google.com',
    'clients4.google.com',
    'clients5.google.com',
    'www.bit.ly',
    'bit.ly',
    'ow.ly',
    'j.mp',
    'goo.gl',
    'tinyurl.com',
    'msftncsi.com',
    'www.msftncsi.com',
    'ea.com',
    'cdn.optimizely.com',
    'res.cloudinary.com',
    'gravatar.com',
    'rover.ebay.com',
    'imgs.xkcd.com',
    'netflix.com',
    'alluremedia.com.au',
    'tomshardware.com',
    'ocsp.apple.com',
    's.shopify.com',
    'keystone.mwbsys.com',
    'dl.dropbox.com',
    'api.ipify.org',
)


def download_if_empty(name: str, url: str):
    if os.path.isfile(name):
        return
    print('Downloading', url)
    req = Request(url=url, headers={'User-Agent': 'curl/7.70.0'})  # some blocks urllib
    r = urlopen(req)
    assert r.status == 200
    write_file(name, r.read())
    pass


def write_file(path, content: bytes):
    with open(path, 'wb') as f:
        f.write(content)
    pass


def filter_before_line(content: List[str], line: str):
    xs = []
    passing = True
    for x in content:
        if not passing:
            xs.append(x)
        else:
            if x == line:
                passing = False
            pass
    return xs


def is_ipaddress(x: str):
    if x.count('.') == 3 and re.match(r'^\d+[.]\d+[.]\d+[.]\d+$', x):
        return True
    try:
        ipaddress.ip_address(x)
        return True
    except Exception:
        return False


def has_special_chars(x: str):
    return re.findall(r'[^0-9a-zA-Z._\-]', x)


def parse_domains(x: str):
    return [
        y.lower()
        for y in x.split(' ')
        for z in [y.strip()]
        if z
        if not z.endswith('.')
        if not is_ipaddress(z)
        if not has_special_chars(z)
    ]


def filter_comments(line: str):
    # input could be anything
    # '# comment'
    # '0.0.0.0 adelogs.adobe.com  # blah'
    line = line.strip()
    if '#' in line:
        line = line[:line.find('#')].strip()
    return [line] if line else []


def mk_cache_filename(url: str):
    return re.sub(r'\W+', '_', url)


def read_file(path):
    with open(path, 'r') as f:
        return f.read()


def download_parse_list(url: str, startfrom: Optional[str] = None):
    print('Parsing', url)
    name = mk_cache_filename(url)
    download_if_empty(name, url)
    content = read_file(name)
    content = content.splitlines(keepends=False)
    if startfrom is not None:
        content = filter_before_line(content, startfrom)
    return [
        domain
        for line in content
        for line1 in filter_comments(line)
        for domain in parse_domains(line1)
    ]


def write_block_file(domains: List[str]):
    with open('block.conf', 'w') as f:
        f.write('\n')
        for x in domains:
            f.write('local-zone: "%s" redirect\n' % x)
            f.write('local-data: "%s 10 IN A 0.0.0.0"\n' % x)
            f.write('\n')
    pass


def print_help():
    print(
        '\nUseful commands'
        '\n  `unbound-checkconf /etc/unbound/unbound.conf`'
        '\n  `unbound-control reload`'
        '\n  `unbound-control stats | grep total.num`'
    )


def main():
    domains = set()
    for x in source_lists:
        xs = download_parse_list(*x)
        print('Got %d domains' % len(xs))
        domains = domains.union(set(xs))
    domains = [
        x
        for x in domains
        if x not in whitelist_domains
    ]
    print('Blocking %d domains total' % len(domains))
    write_block_file(domains)
    print_help()


if __name__ == '__main__':
    main()
