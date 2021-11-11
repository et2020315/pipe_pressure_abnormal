from arcgis_api import arcgis_api_request, UES_API_URL, UESMapServer
from common_utils import merge_dicts

# objects ids for a subgraph of for hot domestic waters
object_ids_testing_subgraph = \
    [824, 827, 856, 859, 843,
     841, 849, 847, 861, 865,
     762, 765, 763, 867, 768,
     772, 773]

MAX_OBJECTS_FROM_REQUEST = 2000


def numbers_to_str_list(numbers):
    return ",".join([str(i) for i in numbers])


def get_testing_subgraph_polylines(MapServerID=UESMapServer.DOMESTIC_COLD_WATER,
                                   URL=UES_API_URL,
                                   query={"where": "1=1"}):
    # ask the server directly for the number of objects in the request
    count = int(arcgis_api_request(
        URL, MapServerID, query=merge_dicts(query, {"returnCountOnly": "true"}),
    ).json()["count"])

    polylines = []
    # breaks down the request becase there is a 2000 request limit, this range object is [0, 2000, 4000, ...]
    for request_size in range(0, count, MAX_OBJECTS_FROM_REQUEST):
        request_json = arcgis_api_request(
            URL,
            MapServerID,
            # get the objectIds into a string in the form "X,Y,Z"
            query=merge_dicts(query, {"resultOffset": str(request_size)}),
            printurl=True
        ).json()
        for group in request_json["features"]:
            if "geometry" in group and len(group["geometry"]["paths"]):
                polylines.append(group["geometry"]["paths"][0])

    return polylines


# example usage:
if __name__ == "__main__":
    print(get_testing_subgraph_polylines())
