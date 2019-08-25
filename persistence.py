from redis import StrictRedis
from redis import ConnectionError


r = StrictRedis(host='localhost', port=6379, db=0)


def get_id(key):
    return r.incr("ids:" + key)


def configure_event_names(events):
    r.sadd("events:types", *events)


def store_days(days):
    seq = range(0,days)
    for i in seq:
        r.sadd("days", i)


def clear_db():
    patterns = ["days*", "miners*", "links*", "events*", "blocks*", "ids*"]
    for pattern in patterns:
        keys = r.keys(pattern)
        for key in keys: r.delete(key)