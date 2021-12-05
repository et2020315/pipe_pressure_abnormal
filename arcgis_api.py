from enum import Enum
import requests
import html
from common_utils import merge_dicts
import os
from urllib.parse import urlparse
from os.path import exists
import json
import geopandas as gpd
from anomaly import dhw_validate_and_predict

MAX_OBJECTS_FROM_REQUEST = 2000
UES_API_URL = "https://ues-arc.tamu.edu/arcgis/rest/services/Yoho/UES_Operations/MapServer/"
TAMU_BASEMAP_API_URL = "https://gis.tamu.edu/arcgis/rest/services/FCOR/TAMU_BaseMap/MapServer/"
APP_DIR = "" # needs to be set up when starting the APP
MAP_CACHE_DIR = os.path.join("data", "map_cache")

# arcgis map servers
class UESMapServer(Enum):
    DOMESTIC_COLD_WATER = 1
    DOMESTIC_HOT_WATER = 11
    THERMAL_CHILLED_WATER = 14
    THERMAL_HEATING_HOT_WATER = 16


# contains the map servers numbers for the university buildings
class TAMUBaseMapServer(Enum):
    UNIV_BUILDING_LESS_3000 = 2
    UNIV_BUILDING_3001_18000 = 3
    SMALL_UNIV_BUILDING_LESS_3000 = 4
    SMALL_UNIV_BUILDING_3001_1800 = 5
    SMALL_UNIV_BUILDING_18001_36000 = 6
    NON_UNIV_BUILDING = 7


def arcgis_api_request(base_api_url, server_num, query={}, printurl = False):
    # encode the query map into a html query string, we may need to escape some characters
    querystr = "".join([ "&" + key + "=" + html.escape(query[key].replace("=", "%3D")) for key in query.keys()])
    # print("QueryStr: ", querystr)
    url = base_api_url + str(server_num.value) + "/query?" + querystr + "&f=pjson"
    if printurl:
        print("URL:", url)
    try:
        return requests.get(url)
    except:
        print("Error on request at", url)
        return None


def get_buildings_with_leaks(time_cutoff_left, detection_method, df ,all_buildings):
    gdf = get_buildings_from_request(server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000)

    has_leak = []
    for item in all_buildings['buildings']:
        data = dhw_validate_and_predict(item["name"], df, [detection_method], time_cutoff_left)
        if data['last_day_has_leak']: has_leak.append(item['id'])

    gdf = gdf[gdf['OBJECTID'].isin(has_leak)]

    return gdf

# this function bypasses the 2000 limit of objectids that can be obtained by a single request
# it breaks down the request because there is a 2000 request limit, this range object is [0, 2000, 4000, ...]
# it will store the geojson locally and then it returns the location of this geojson (a string)
# it caches the request into a file in MAP_CACHE_DIR
def unlimited_arcgis_api_request_json(base_api_url=UES_API_URL,
                                      server_num=UESMapServer.DOMESTIC_COLD_WATER,
                                      query={"where": "1=1"}, printurl = True):
    # the following caches into a json file the call so that in future calls this request is faster
    # the naming of the json is like so: the domain - server number - query string
    global APP_DIR, MAP_CACHE_DIR
    url_domain_only = urlparse(base_api_url).netloc
    query_str_simplified = "".join([e + "-" + str(query[e]) for e in query])
    filename_cache =r"{:}_{:}_{:}.txt".format(url_domain_only, server_num.value, query_str_simplified)
    file_location = os.path.join(APP_DIR, MAP_CACHE_DIR, filename_cache)

    if exists(file_location):
        # don't do anything, the file is already loaded to map_cache folder
        pass
    else:
        # ask the server directly for the number of objects in the request
        count = int(arcgis_api_request(
            base_api_url, server_num, query=merge_dicts(query, {"returnCountOnly": "true"}), printurl=printurl
        ).json()["count"])

        # compiles the requests with different resultOffset [0, 2000, 4000, ...] into final_result_json
        for request_size in range(0, count, MAX_OBJECTS_FROM_REQUEST):
            request_json = arcgis_api_request(
                base_api_url,
                server_num,
                query=merge_dicts(query, {"resultOffset": str(request_size)}),
                printurl=printurl
            ).json()

            # the header is only copied from the first iteration
            if request_size == 0:
                final_result_json = request_json
            else:
                final_result_json["features"] += request_json["features"]

        # write the json to the cached file for future calls
        with open(file_location, 'w') as file:
            file.write(json.dumps(final_result_json))

    return file_location


def get_lines_from_request(base_api_url=UES_API_URL,
                           server_num=UESMapServer.DOMESTIC_COLD_WATER,
                           query={"where": "1=1", "outFields":"objectid"}):
    file_name_geojson = unlimited_arcgis_api_request_json(
        base_api_url, server_num, query=query
    )
    gdf = gpd.read_file(file_name_geojson)
    gdf = gdf.to_crs('epsg:4326')

    return gdf


def get_buildings_from_request(base_api_url=TAMU_BASEMAP_API_URL,
                               server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000,
                               query={"text": "Hall", "outFields": "objectid"}):
    file_name_geojson = unlimited_arcgis_api_request_json(
        base_api_url, server_num, query=query
    )

    gdf = gpd.read_file(file_name_geojson)
    gdf = gdf.to_crs('epsg:4326')

    return gdf


if __name__ == "__main__":
    #**********example usages
    #testing with hot water
    hot_pipes_filename = arcgis_api_request(UES_API_URL, UESMapServer.DOMESTIC_HOT_WATER, {"where": "1=1", "outFields": "objectid", "resultOffset": "8000"}, True).json()["features"]
    features_filename = arcgis_api_request(TAMU_BASEMAP_API_URL, TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, {"text": "Hall", "outFields": "objectid"}, True).json()["features"]

    # convert from projected coordinates to coordinate system (testing for now)
