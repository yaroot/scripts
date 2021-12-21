#!/usr/bin/env python3
import json
import os
import sys


def write(path, content):
    path = './contract/' + path.lstrip('/')
    print(f'Writing {path}')
    dir = os.path.dirname(path)
    os.makedirs(dir, mode=0o755, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    pass


def main():
    source_path = sys.argv[1]
    with open(source_path, 'r') as f:
        source_resp = json.load(f)
    result = source_resp['result']
    for xr in result:
        source_code = xr['SourceCode']
        if source_code.startswith('{{'):
            source_code = source_code[1:]
        if source_code.endswith('}}'):
            source_code = source_code[:-1]
        sources = json.loads(source_code)['sources']
        for x, v in sources.items():
            code = v['content']
            write(x, code)
    pass


if __name__ == '__main__':
    main()

