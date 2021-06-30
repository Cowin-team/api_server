import time
import json
import redis
import requests

r = redis.Redis()

res = json.loads(r.get('resources'))

for city, details in res.items():
	for resource, sheet_id in details.items():
		resp = requests.post('http://127.0.0.1:8080/data/upsert', json={'sheet_id': sheet_id})

		if resp.status_code == 200:
			print(f'Upserted. City: [{city}] Resource: [{resource}]')
		else:
			print(f'Failed. City: [{city}] Resource: [{resource}] StatusCode: [{str(resp.status_code)}]')

		time.sleep(2)

