import flask
from flask import request, jsonify
from flask_cors import CORS


import sheet
import resources


app = flask.Flask(__name__)
CORS(app)

sheet.init()
resources.init()


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


@app.route('/resource/get_coordinates', methods=['GET'])
def get_coordinates():
    return jsonify(resources.get_coordinates()), 200


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
