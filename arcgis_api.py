from enum import Enum
import requests
import html
import pyproj
from pyproj import transform, Transformer

UES_API_URL = "https://ues-arc.tamu.edu/arcgis/rest/services" + "/Yoho/UES_Operations/MapServer/"
TAMU_BASEMAP_API_URL = "https://gis.tamu.edu/arcgis/rest/services/FCOR/TAMU_BaseMap/MapServer/"
POST_FIX = "/query?"


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


def convertToLatLng(x1, y1):
    transformer = Transformer.from_crs('epsg:32139', 'epsg:4326')
    x2, y2 = transformer.transform(x1, y1)

    return x2, y2


def arcgis_api_request(base_api_url, ServerNum, query={}, printurl = False):
    # encode the query map into a html query string, we may need to escape some characters
    querystr = "".join([ "&" + key + "=" + html.escape(query[key].replace("=", "%3D")) for key in query.keys()])
    url = base_api_url + str(ServerNum.value) + POST_FIX + querystr + "&f=pjson"
    if printurl:
        print("URL:", url)
    try:
        return requests.get(url)
    except:
        print("Error on request at", url)
        return None


if __name__ == "__main__":
    #**********example usages
    #testing with hot water
    hot_pipes_dict = arcgis_api_request(UES_API_URL, UESMapServer.DOMESTIC_HOT_WATER, {"where": "1=1", "outFields": "objectid"}, True).json()["features"]

    features_dict = arcgis_api_request(TAMU_BASEMAP_API_URL, TAMUBaseMapServer.UNIV_BUILDING_LESS_3000, {"text": "Hall", "outFields": "objectid"}, True).json()["features"]

    # convert from projected coordinates to coordinate system (testing for now)


    #for feature in features_dict:
        #print(feature["geometry"]['rings'])



    # testing with domestic cold water
    #print(arcgis_api_request(UES_API_URL, UESMapServer.DOMESTIC_COLD_WATER, {"where": "1=1"}).json())

