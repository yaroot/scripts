#!/usr/bin/python

# https://api.slack.com/custom-integrations/legacy-tokens

import os
import time
import requests

http = requests.session()

TOKEN = os.environ['TOKEN']
USER = os.environ['SLACK_USER']


# https://api.slack.com/methods/files.list
def list_files():
    params = {
        'token': TOKEN,
        'count': 100,
        'ts_to': int(time.time()) - 24*3600*30,
        'user': USER
    }
    r = http.get('https://slack.com/api/files.list', params=params)
    j = r.json()
    assert j['ok']
    return j['files']
    pass


# https://api.slack.com/methods/files.delete
def remove_file(x):
    _id = x['id']
    params = {
        'token': TOKEN,
        'file': _id
    }
    r = http.post('https://slack.com/api/files.delete', params=params)
    print(_id, r)


def main():
    files = list_files()
    for x in files:
        remove_file(x)


if __name__ == '__main__':
    main()
