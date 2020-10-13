#!/usr/bin/env python3

import os
import sys
import json
import requests

http = requests.Session()


def download(url):
    r = http.get(url)
    assert r.ok
    return r.text


def read_searchindex(content):
    a = content.index('[')
    b = content.index(']')
    content = (content[a: b+1])
    files = json.loads(content)
    return files


def main(base_url):
    base_url = base_url.rstrip('/')
    searchindex = download(f'{base_url}/searchindex.js')
    files = read_searchindex(searchindex)
    for path in files:
        bp = os.path.dirname(path)
        # os.makedirs(f'./{path}')
        print(f'>> {path}')
        if bp:
            os.makedirs(f'./{bp}', exist_ok=True)
        content = download(f'{base_url}/{path}.html')
        with open(f'./{path}.html', 'w') as f:
            f.write(content)


if __name__ == '__main__':
    main(sys.argv[1])

