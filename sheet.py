import json
import time
import requests
import redis


import resources


API_KEY = 'AIzaSyClGVndCtMIDvZ7GdE1fO5OPQL5XdtMvVM'
SHEET_URL = 'https://sheets.googleapis.com/v4/spreadsheets/%s/values/Sheet1!A2:Q?key=%s'
REDIS = None


LAST_UPDATED = '%s_%s_last_updated'
DATA = '%s_%s_data'


def init():
    global REDIS
    REDIS = redis.Redis()


def sync():
    pass


def get(city, resource):
    """ Given a city and the type of resource needed (beds/oxygen)
    fetching it from the cache or from the google sheet """

    if not city:
        return {'msg': 'city not provided'}, 401

    if not resource:
        return {'msg': 'resource not provided'}, 401

    last_updated_key = LAST_UPDATED % (city, resource)
    data_key = DATA % (city, resource)

    try:
        # Returning from cache if the data was updated in the last 5 mins
        if time.time() - float(REDIS.get(last_updated_key)) < 300:
            values = REDIS.get(data_key).decode('utf-8')
            return json.loads(values), 200
    except Exception as e:
        pass

    sheet_link = resources.get_sheet_link(city, resource)

    if not sheet_link:
        return {'msg': '%s not found for %s' % (resource, city)}, 404

    url = SHEET_URL % (sheet_link, API_KEY)
    resp = requests.get(url)

    if resp.status_code == 200:
        values = resp.json()['values']

        REDIS.set(last_updated_key, time.time())
        REDIS.set(data_key, json.dumps(values))

        return values, 200

    return {'msg': 'something went wrong'}, 500
