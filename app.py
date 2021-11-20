import json

from flask import Flask
from flask_cors import CORS
from arcgis_api import convertToLatLng, UESMapServer, get_polylines_from_request
from plot_water import get_HDW_for_building
import os

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

@app.route('/get_all_buildings')
def all_buildings():
    return { "buildings": [
        {"name": "KiestHall_Supply"},
        {"name": "FountainHall_Supply"},
        {"name": "GainerHall_Supply"},
        {"name": "LacyHall_Supply"},
        {"name": "HarrellHall_Supply"},
        {"name": "WhiteHall_Supply"},
        {"name": "HarringtonHall_Supply"},
        {"name": "SpenceHall_Return"},
        {"name": "BriggsHall_Return"},
        {"name": "WhitelyHall_Return"},
        {"name": "HarringtonHall_Return"},
        {"name": "WellsResidenceHall_Supply"},
        {"name": "EpprightResidenceHall_Supply"},
        {"name": "UnderwoodResidenceHall_Supply"},
        {"name": "DuncanDiningHall_Supply"},
    ]}


@app.route("/get_pressure_data_for/<building>/<time_period>")
def get_pressure_data_for(building, time_period):
    return get_HDW_for_building(
        os.path.join(app.root_path, "data/pressures_domestic_hot.csv"),
        building,
        time_period
    )


if __name__ == '__main__':
    app.run(debug=True)

#first algorithm flags everything after 3 hours
# it is showing everything that is outside the bounds
# it is not bad to flag everything
