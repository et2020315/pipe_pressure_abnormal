import json

from flask import Flask
from flask_cors import CORS
from arcgis_api import convertToLatLng, UESMapServer
from testing_data import get_testing_subgraph_polylines

app = Flask(__name__)

CORS(app)

@app.route('/')
def hello_world():  # put application's code here
    return {
        'name' : ["item1", "item2"]
    }

@app.route('/test_pipes')
def test_pipes():
    testing_subgraph_polylines = get_testing_subgraph_polylines(MapServerID=UESMapServer.DOMESTIC_COLD_WATER)
    new_polylines = []
    for item in testing_subgraph_polylines:
        new_polylines.append([])
        for pair in item:
            coords = convertToLatLng(pair[0], pair[1])
            new_polylines[len(new_polylines) - 1].append({'lat': coords[0], 'lng': coords[1]})


    return { 'data': new_polylines}


if __name__ == '__main__':
    app.run(debug=True)
