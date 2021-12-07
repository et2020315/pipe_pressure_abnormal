from flask import Flask
from flask_cors import CORS
from flask import request

import arcgis_api
from arcgis_api import UESMapServer, get_lines_from_request, TAMUBaseMapServer, get_buildings_from_request
import os
import pandas as pd
from anomaly import dhw_validate_and_predict, refine_dataframe

app = Flask(__name__)
df = pd.read_csv(os.path.join(app.root_path, "data/finalDHW.csv"))
df = refine_dataframe(df)

CORS(app)
arcgis_api.APP_DIR = app.root_path


@app.route('/')
def hello_world():  # put application's code here
    return {
        'data' : "Welcome to pipe-leak's API!"
    }


@app.route('/domestic_hot_water')
def domestic_hot_water():
    gdf = get_lines_from_request(server_num=UESMapServer.DOMESTIC_HOT_WATER)
    gdf['color'] = "red"
    gdf['requestName'] = "dhw"
    return gdf.to_json()


@app.route('/domestic_cold_water')
def domestic_cold_water():
    gdf = get_lines_from_request(server_num=UESMapServer.DOMESTIC_COLD_WATER)
    gdf['color'] = "blue"
    gdf['requestName'] = "dcw"
    return gdf.to_json()


@app.route('/buildings')
def buildings():
    gdf = get_buildings_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000)
    gdf['color'] = "orange"
    gdf['requestName'] = "blds"
    gdf['fillColor'] = "orange"
    return gdf.to_json()


@app.route('/buildings_with_leaks')
def buildings_with_leaks():
    gdf = arcgis_api.get_buildings_mapdata_with_leaks(
        request.args.get('time_cutoff_left'),
        request.args.get('detection_method'),
        df,
        get_all_buildings())
    gdf['color'] = "red"
    gdf['requestName'] = "blds_with_leaks"
    gdf['fillColor'] = "purple"
    gdf['fillOpacity'] = 1.0
    gdf['zIndex'] = 1

    return gdf.to_json()


@app.route('/buildings_with_leak_indicators/<building_name>')
def buildings_with_leak_indicators(building_name):
    data = dhw_validate_and_predict(building_name, df, [request.args.get('detection_method')], request.args.get('time_cutoff_left'))

    return {"last_day_has_leak": data["last_day_has_leak"]}


@app.route('/center_of_buildings_with_leaks')
def center_of_buildings_with_leaks():
    gdf = arcgis_api.get_buildings_mapdata_with_leaks(
        request.args.get('time_cutoff_left'),
        request.args.get('detection_method'),
        df,
        get_all_buildings())

    bounds = gdf.total_bounds
    return { "lat": (bounds[3] - bounds[1])/2.0 + bounds[1],
             "lng" : (bounds[2] - bounds[0])/2.0 + bounds[0] }


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
def get_all_buildings():
    return { "buildings": [
        {"name": "KiestHall_Supply", "id": 57},
        {"name": "FountainHall_Supply", "id": 78},
        {"name": "GainerHall_Supply", "id": 70},
        {"name": "LacyHall_Supply", "id": 308},
        {"name": "HarrellHall_Supply", "id": 59},
        {"name": "WhiteHall_Supply", "id": 978},
        {"name": "HarringtonHall_Supply", "id": 981},
        {"name": "SpenceHall_Return", "id": 56},
        {"name": "BriggsHall_Return", "id": 65},
        {"name": "WhitelyHall_Return", "id": 980},
        {"name": "HarringtonHall_Return", "id": 981},
        {"name": "WellsResidenceHall_Supply", "id": 660},
        {"name": "EpprightResidenceHall_Supply", "id": 677},
        {"name": "UnderwoodResidenceHall_Supply", "id": 66},
        {"name": "DuncanDiningHall_Supply", "id": 688},
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
