import flask
from flask import request, jsonify
from flask_cors import CORS
from operator import itemgetter


import sheet
import resources
import database as resource_store


app = flask.Flask(__name__)
CORS(app)

sheet.init()
resources.init()
#resource_store.init()

@app.route('/data/fetch', methods=['GET'])
def fetch_data():

    resource = request.args.get('resource')

    # expecting bounding coordinates as pt{i}=latitude,longitude (EX: pt1=12.1,98.01&pt2=14.1,73.94&...)
    bounding_points = []
    for i in range(4):
        bounding_points.append(request.args.get(f'pt{i + 1}'))
    bounding_points = filter(lambda x: x is not None, bounding_points) # removing none values
    bounding_points = map(lambda x: (float(x.split(',')[0]), float(x.split(',')[1])), bounding_points) # converting strings to floats
    bounding_points = list(bounding_points)

    data = resource_store.get(resource_type=resource, bounding_points=bounding_points)

    return jsonify(data)


@app.route('/data/upsert', methods=['POST'])
def upsert_data():

    try:
        google_sheet_id = request.json['sheet_id']
        sheet_info = resource_store.get_sheet_info(google_sheet_id)
        city, resource_type = itemgetter('city', 'resource_type')(sheet_info)
        resource_info = resource_store.get_sheet_data(google_sheet_id, resource_store.API_KEY)
    except Exception as err:
        return f"Invalid sheet_id: {request.json.get('sheet_id') if isinstance(request.json, object) else ''}", 417

    resource_store.upsert(city, resource_type, resource_info, google_sheet_id)
    
    return "Successfull"

@app.route('/sheet/fetch', methods=['GET'])
def fetch_sheet():
    city = request.args.get('city').lower()
    resource = request.args.get('resource').lower()
    data, status_code = sheet.get(city, resource)
    return jsonify(data), status_code


@app.route('/sheet/sync', methods=['POST'])
def sync():
    sheet.sync()


@app.route('/resource/get', methods=['GET'])
def get_resource():
    return jsonify(resources.get()), 200


@app.route('/resource/get_details', methods=['GET'])
def get_details():
    return jsonify(resources.get_details()), 200


@app.route('/resource/update', methods=['POST'])
def update_resource():
    try:
        city = request.json.get('city').lower()
        resource = request.json.get('resource').lower()
        link = request.json.get('link')

        if not city:
            return jsonify({'msg': 'city not provided'}), 401

        if not resource:
            return jsonify({'msg': 'resource not provided'}), 401

        if not link:
            return jsonify({'msg': 'link not provided'}), 401

        resources.update(city, resource, link)
        return jsonify({'msg': 'success'}), 201
    except Exception as e:
        return jsonify({'msg': 'failed', 'err': str(e)}), 500
