#!/usr/bin/env python

import os
import sys
import httpx

client = httpx.Client()

ENDPOINT = os.environ.get('ELASTIC_BASE', 'http://localhost:9200').rstrip('/')


def _list_indices():
    r = client.get(f'{ENDPOINT}/_cat/indices', params=dict(format='json'))
    return [
        x['index']
        for x in r.json()
    ]


def _list_shards():
    r = client.get(f'{ENDPOINT}/_cat/shards', params=dict(format='json'))
    xs = []
    for x in r.json():
        xs.append((x['index'], x['shard'], x['node']))
    return xs


def list_indices():
    r = client.get(f'{ENDPOINT}/_cat/indices', params=dict(format='json'))
    print('{:30}  {:>8}  {:>6}  {:>8}  {:>6}  {:>6}'.format(*'index,size,count,deleted,status,health'.split(',')))
    xs = r.json()
    xs = sorted(xs, key=lambda x: x['index'])
    for a in xs:
        index = a['index']
        size = a['store.size']
        count = a['docs.count']
        deleted = a['docs.deleted']
        status = a['status']
        health = a['health']
        print('{:30}  {:>8}  {:>6}  {:>8}  {:>6}  {:>6}'.format(index, size, count, deleted, status, health))
    pass


def get_settings(index):
    r = client.get(f'{ENDPOINT}/{index}/_settings')
    resp = r.json()
    sts = resp[index]['settings']['index']
    sts = [
        (k, v)
        for k, v in sts.items()
    ]
    sts = sorted(sts, key=lambda x: x[0])
    for k, v in sts:
        print('{:30}  {}'.format(k, str(v)))


def set_index(index, name, value):
    v = value
    try:
        v = int(v)
    except Exception:
        try:
            v = float(v)
        except Exception:
            pass
        pass

    indices = [index]
    if index == '_all':
        indices = _list_indices()
        pass

    for index in indices:
        settings = {name: v}
        r = client.put(f'{ENDPOINT}/{index}/_settings', json=settings)
        print(index, r.status_code, settings)
    pass


def disable_shard_allocation():
    r = client.put(f'{ENDPOINT}/_cluster/settings', json={
        'transient': {'cluster.routing.allocation.enable': 'none'}
    })
    print('disable shard allocation', r.status_code)


def enable_shard_allocation():
    r = client.put(f'{ENDPOINT}/_cluster/settings', json={
        'transient': {'cluster.routing.allocation.enable': None}
    })
    print('enable shard allocation', r.status_code)


def relocate_shards(node):
    for index, shard, node0 in _list_shards():
        if node0 == node: continue
        r = client.post(f'{ENDPOINT}/_cluster/reroute', json={
            'commands': [
                {
                    'move': {
                        'index': index,
                        'shard': shard,
                        'from_node': node0,
                        'to_node': node,
                    }
                },
            ],
        })
        print('move', r.status_code, index)
    pass


def usage():
    print('Usage: ')
    print(' ls                              -- list indices')
    print(' settings [index]                -- get index configuration')
    print(' set [index] [name] [value]      -- set index configuration')
    print(' disable-shard-allocation        -- disable shard allocation')
    print(' enable-shard-allocation         -- enable shard allocation')
    print(' relocate-shards [node]          -- relocate all shards to [node]')


def main():
    args = sys.argv[1:]
    if len(args) == 0 or '-h' in args:
        usage()
        return
    action = args[0]
    args0 = args[1:]
    print(f'.. Using {ENDPOINT}')

    if action == 'ls':
        list_indices()
    elif action == 'settings':
        get_settings(*args0)
    elif action == 'set':
        set_index(*args0)
    elif action == 'disable-shard-allocation':
        disable_shard_allocation()
    elif action == 'enable-shard-allocation':
        enable_shard_allocation()
    elif action == 'relocate-shards':
        relocate_shards(*args0)
    else:
        # TODO
        #   https://www.elastic.co/guide/en/elasticsearch/reference/current/add-elasticsearch-nodes.html
        #   POST /_cluster/voting_config_exclusions?node_names=node_name
        usage()
    pass


if __name__ == '__main__':
    main()


