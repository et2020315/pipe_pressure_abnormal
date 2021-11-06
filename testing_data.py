from arcgis_api import arcgis_api_request, UES_API_URL, UESMapServer

# objects ids for a subgraph of for hot domestic waters
object_ids_testing_subgraph = \
    [824, 827, 856, 859, 843,
     841, 849, 847, 861, 865,
     762, 765, 763, 867, 768,
     772, 773]


def get_testing_subgraph_polylines():
    polylines = []

    request_json = arcgis_api_request(
        UES_API_URL,
        UESMapServer.DOMESTIC_HOT_WATER,
        # get the objectIds into a string in the form "X,Y,Z"
        {"objectIds": ",".join([str(i) for i in object_ids_testing_subgraph])}
    ).json()
    for group in request_json["features"]:
        polylines.append(group["geometry"]["paths"][0])

    return polylines


# example usage:
if __name__ == "__main__":
    print(get_testing_subgraph_polylines())
