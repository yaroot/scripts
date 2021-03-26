from .util import load_api
import sys
import requests
import json
import time


def main():
    api = load_api()
    session = requests.session()
    session.auth = api.auth
    print(session.auth)
    for line in sys.stdin.readlines():
        twt = json.loads(line)
        _id = twt[0]
        print(twt)
        int(_id)
        r = session.post(f'https://api.twitter.com/1.1/statuses/destroy/{_id}.json')
        print(r)
        if r.status_code not in (200, 404): return
        time.sleep(1)
    pass


if __name__ == '__main__':
    main()