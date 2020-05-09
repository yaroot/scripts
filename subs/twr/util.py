from TwitterAPI import TwitterAPI
from subs import config


def load_api():
    twitter = TwitterAPI(
        config.CONSUMER_KEY,
        config.CONSUMER_SECRET,
        config.ACCESS_TOKEN_KEY,
        config.ACCESS_TOKEN_SECRET)
    return twitter


# twitter snowflake:
# 41 bits of timestamp in millis
# 10 bits of machine id
# 12 bits of sequence id
def timestamp_from_id(id: int):
    MASK = 9223372036850581504
    EPOCH = 1288834974657
    return (((id & MASK) >> 22) + EPOCH)/1000

