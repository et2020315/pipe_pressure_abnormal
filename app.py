import json

from flask import Flask
from flask_cors import CORS
from arcgis_api import convertToLatLng, UESMapServer
from flask import request
from plot_water import get_df
from arcgis_api import convertToLatLng, UESMapServer, get_polylines_from_request, TAMUBaseMapServer, TAMU_BASEMAP_API_URL, get_polygons_from_request
from plot_water import get_HDW_for_building
import os
import pandas as pd
from anomaly import dhw_validate_and_predict
from anomaly import modified_anomaly

app = Flask(__name__)

df = pd.read_csv(os.path.join(app.root_path, "data/finalDHW.csv"))

CORS(app)

@app.route('/')
def hello_world():  # put application's code here
    return {
        'name' : "Welcome to pipe-leak's API!"
    }

@app.route('/test_pipes')
def test_pipes():
    testing_subgraph_polylines = get_polylines_from_request(server_num=UESMapServer.DOMESTIC_HOT_WATER)

    return { 'data': testing_subgraph_polylines}

@app.route('/test_cold_pipes')
def test_cold_pipes():
    testing_subgraph_polylines_cold = get_polylines_from_request(server_num=UESMapServer.DOMESTIC_COLD_WATER)

    return { 'data': testing_subgraph_polylines_cold}
@app.route('/test_buildings')
def test_building():
    testing_subgraph_polylines_buildings = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000)
    return {'data': testing_subgraph_polylines_buildings}

@app.route('/test_affected_buildings')
def test_affected_buildings():
    testing_subgraph_polylines_affected_buildings = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "57, 78, 70, 308, 59, 978, 981, 56, 65, 980, 660, 677, 66, 688", "outFields" : "objectid"})
    return {'data': testing_subgraph_polylines_affected_buildings}

@app.route('/test_affected_kiest')
def test_affected_kiest():
    testing_subgraph_affected_kiest = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "57", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_kiest}

@app.route('/test_affected_fountain')
def test_affected_fountain():
    testing_subgraph_affected_fountain = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "78", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_fountain}

@app.route('/test_affected_gainer')
def test_affected_gainer():
    testing_subgraph_affected_gainer = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "70", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_gainer}

@app.route('/test_affected_lacy')
def test_affected_lacy():
    testing_subgraph_affected_lacy = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "308", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_lacy}

@app.route('/test_affected_harrell')
def test_affected_harrell():
    testing_subgraph_affected_harrell = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "59", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_harrell}

@app.route('/test_affected_white')
def test_affected_white():
    testing_subgraph_affected_white = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "978", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_white}

@app.route('/test_affected_harrington')
def test_affected_harrington():
    testing_subgraph_affected_harrington = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "981", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_harrington}

@app.route('/test_affected_spence')
def test_affected_spence():
    testing_subgraph_affected_spence = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "56", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_spence}

@app.route('/test_affected_briggs')
def test_affected_briggs():
    testing_subgraph_affected_briggs = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "65", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_briggs}

@app.route('/test_affected_whiteley')
def test_affected_whiteley():
    testing_subgraph_affected_whiteley = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "980", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_whiteley}

@app.route('/test_affected_wells')
def test_affected_wells():
    testing_subgraph_affected_wells = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "660", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_wells}

@app.route('/test_affected_eppright')
def test_affected_eppright():
    testing_subgraph_affected_eppright = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "677", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_eppright}

@app.route('/test_affected_underwood')
def test_affected_underwood():
    testing_subgraph_affected_underwood = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "66", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_underwood}

@app.route('/test_affected_duncan')
def test_affected_duncan():
    testing_subgraph_affected_duncan = get_polygons_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, query={"objectIds" : "688", "outFields" : "objectid"})
    return {'data' : testing_subgraph_affected_duncan}

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


@app.route("/get_pressure_data_for/<building>")
def get_pressure_data_for(building):
    time_cutoff_left = request.args.get('time_cutoff_left')
    detection_method = request.args.get('detection_method')
    data = dhw_validate_and_predict(building, df, [detection_method], time_cutoff_left)
    return data

@app.route("/get_building_map_data_for/<building>")
def get_building_map_data_for(building):
    time_cutoff_left = request.args.get('time_cutoff_left')
    detection_method = request.args.get('detection_method')
    data = dhw_validate_and_predict(building, df, [detection_method], time_cutoff_left)
    return data

if __name__ == '__main__':
    app.run(debug=True)

#first algorithm flags everything after 3 hours
# it is showing everything that is outside the bounds
# it is not bad to flag everything
