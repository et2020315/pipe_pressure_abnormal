from arcgis_api import arcgis_api_request, UES_API_URL, UESMapServer

# objects ids for a subgraph of for hot domestic waters
object_ids_testing_subgraph = \
    [824, 827, 856, 859, 843,
     841, 849, 847, 861, 865,
     762, 765, 763, 867, 768,
     772, 773]

def numbers_to_str_list(numbers):
    return ",".join([str(i) for i in numbers])

def get_testing_subgraph_polylines(object_ids_testing_subgraph = [], MapServerID = UESMapServer.DOMESTIC_COLD_WATER):
    polylines = []
    iteration = 1
    query_str = "0"
    query_int = 0
    repeat = True
    total_skipped = 0
    while repeat == True:
        skipped_counter = 0
        # print("New query_str value is: ", query_str)
        request_json = arcgis_api_request(
            UES_API_URL,
            MapServerID,
            # get the objectIds into a string in the form "X,Y,Z"
            query=
                {"objectIds": numbers_to_str_list(object_ids_testing_subgraph), 'where': "1=1" , 'resultOffset': query_str},
            printurl=True
        ).json()
        for group in request_json["features"]:
            if "geometry" in group:
                if len(group["geometry"]["paths"]) != 0:
                    polylines.append(group["geometry"]["paths"][0])
                else:
                    skipped_counter += 1
            else:
                skipped_counter += 1
        # print("Polylines length: ", len(polylines))
        # print("Skipped lines: ", skipped_counter)
        total_skipped += skipped_counter

        if (len(polylines) + total_skipped) < 2000 * iteration:
            repeat = False
        else:
            query_int += 2000
            query_str = str(query_int)
        iteration += 1
    return polylines


# example usage:
if __name__ == "__main__":
    print(get_testing_subgraph_polylines())
