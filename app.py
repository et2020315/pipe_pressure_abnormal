import json

from flask import Flask
from flask_cors import CORS
from arcgis_api import convertToLatLng, UESMapServer
from testing_data import get_testing_subgraph_polylines
from flask import request
from plot_water import get_df
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

@app.route('/test_data/<general_type>/<subtype>/<building_num>/', methods=['Get'])
def test_data(general_type, subtype, building_num):
    start_date = request.args.get('startdate')
    end_date = request.args.get('enddate')
    # if (subtype == 'CHW'):
    #     # df = get_df(general_type, )
    # elif (subtype == 'HW'):
        # df = get_df(general_type, )
    return {
        'Domestic / Non Domestic Hot /Cold water': general_type,
        'Pressure / Flow rate' : subtype,
        'Building number' : building_num,
        'start date' : request.args.get('startdate'),
        'end_date' : request.args.get('enddate')
        }

if __name__ == '__main__':
    app.run(debug=True)
