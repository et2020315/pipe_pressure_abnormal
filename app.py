import json

from flask import Flask
from flask_cors import CORS
from arcgis_api import convertToLatLng, UESMapServer, get_polylines_from_request

app = Flask(__name__)

CORS(app)

@app.route('/')
def hello_world():  # put application's code here
    return {
        'name' : ["item1", "item2"]
    }

@app.route('/test_pipes')
def test_pipes():
    testing_subgraph_polylines = get_polylines_from_request(server_num=UESMapServer.DOMESTIC_HOT_WATER)

    return { 'data': testing_subgraph_polylines}

@app.route('/test_cold_pipes')
def test_cold_pipes():
    testing_subgraph_polylines_cold = get_polylines_from_request(server_num=UESMapServer.DOMESTIC_COLD_WATER)

    return { 'data': testing_subgraph_polylines_cold}

if __name__ == '__main__':
    app.run(debug=True)
