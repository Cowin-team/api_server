import json
import redis


SRC = {}
REDIS = None


def init():
    global SRC, REDIS

    REDIS = redis.Redis()
    SRC = REDIS.get('resources')

    if SRC is None:
        with open('./resources.json') as resource_file:
            SRC = json.loads(resource_file.read())

        REDIS.set('resources', json.dumps(SRC))
    else:
        SRC = json.loads(SRC)


def update(city, resource, link):
    if city not in SRC:
        SRC[city] = {}

    SRC[city][resource] = link
    REDIS.set('resources', json.dumps(SRC))

    with open('./resources.json', 'w') as resource_file:
        resource_file.write(json.dumps(SRC, indent=4))


def get_sheet_link(city, resource):
    if city not in SRC:
        return None
    if resource not in SRC[city]:
        return None

    return SRC[city][resource]
