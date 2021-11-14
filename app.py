import json

from flask import Flask
from flask_cors import CORS
from arcgis_api import convertToLatLng, UESMapServer
from flask import request
from plot_water import get_df
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

#first algorithm flags everything after 3 hours
# it is showing everything that is outside the bounds
# it is not bad to flag everything
