from enum import Enum
from pathlib import Path

import requests
import html
import pyproj
from pyproj import transform, Transformer
from common_utils import merge_dicts
import os
from urllib.parse import urlparse
from os.path import exists
import json

MAX_OBJECTS_FROM_REQUEST = 2000
UES_API_URL = "https://ues-arc.tamu.edu/arcgis/rest/services" + "/Yoho/UES_Operations/MapServer/"
TAMU_BASEMAP_API_URL = "https://gis.tamu.edu/arcgis/rest/services/FCOR/TAMU_BaseMap/MapServer/"
transformer = Transformer.from_crs('epsg:32139', 'epsg:4326')
transformer2 = Transformer.from_crs('epsg:102100', 'epsg:4326')
APP_DIR = ""
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


def convertToLatLng(x1, y1, conversiontype=0):
    if conversiontype == 0:
        x2, y2 = transformer.transform(x1, y1)
    elif conversiontype == 1:
        x2, y2 = transformer2.transform(x1, y1)

    return x2, y2


def arcgis_api_request(base_api_url, server_num, query={}, printurl = False):
    # encode the query map into a html query string, we may need to escape some characters
    # for i in query.keys():
    #     print(i)
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


# this function bypasses the 2000 limit of objectids that can be obtained by a single request
# it breaks down the request because there is a 2000 request limit, this range object is [0, 2000, 4000, ...]
# it returns a json
# it also caches the request into a file in MAP_CACHE_DIR
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

    final_result_json = {}
    if exists(file_location):
        with open(file_location, 'r') as file:
            final_result_json = json.loads(file.read())
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

        #write the json to the cached file for future calls
        with open(file_location, 'w') as file:
            file.write(json.dumps(final_result_json))

    return final_result_json

def get_polylines_from_request(base_api_url=UES_API_URL,
                                   server_num=UESMapServer.DOMESTIC_COLD_WATER,
                                   query={"where": "1=1", "outFields":"objectid"}):
    request_json = unlimited_arcgis_api_request_json(
        base_api_url, server_num, query=query
    )

    polylines = []
    for group in request_json["features"]:
        if "geometry" in group and len(group["geometry"]["paths"]):
            vertex_data = group["geometry"]["paths"][0]
            polylines.append([])
            for vertex in vertex_data:
                coords = convertToLatLng(vertex[0], vertex[1])
                polylines[len(polylines) - 1].append({'lat': coords[0], 'lng': coords[1], 'id': group["attributes"]['OBJECTID']})


    return polylines

def get_polygons_from_request(base_api_url=TAMU_BASEMAP_API_URL,
                              server_num=TAMUBaseMapServer.UNIV_BUILDING_LESS_3000,
                              query={"text": "Hall", "outFields": "objectid"}):
    request_json = unlimited_arcgis_api_request_json(
        base_api_url, server_num, query=query
    )
    polygons = []
    for group in request_json["features"]:
        if "geometry" in group and len(group["geometry"]["rings"]):
            vertex_data = group["geometry"]["rings"][0]
            polygons.append([])
            for vertex in vertex_data:
                coords = convertToLatLng(vertex[0], vertex[1], conversiontype=1)
                polygons[len(polygons) - 1].append({'lat': coords[0], 'lng': coords[1], 'id': group["attributes"]['OBJECTID']})

    return polygons

if __name__ == "__main__":
    #**********example usages
    #testing with hot water
    hot_pipes_dict = arcgis_api_request(UES_API_URL, UESMapServer.DOMESTIC_HOT_WATER, {"where": "1=1", "outFields": "objectid", "resultOffset": "8000"}, True).json()["features"]
    for i in hot_pipes_dict:
        print(i)
    features_dict = arcgis_api_request(TAMU_BASEMAP_API_URL, TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, {"text": "Hall", "outFields": "objectid"}, True).json()["features"]

    # convert from projected coordinates to coordinate system (testing for now)


    #for feature in features_dict:
        #print(feature["geometry"]['rings'])



    # testing with domestic cold water
    #print(arcgis_api_request(UES_API_URL, UESMapServer.DOMESTIC_COLD_WATER, {"where": "1=1"}).json())

