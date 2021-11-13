from arcgis_api import arcgis_api_request, UES_API_URL, UESMapServer, unlimited_arcgis_api_request_json

# objects ids for a subgraph of for hot domestic waters
object_ids_testing_subgraph = \
    [824, 827, 856, 859, 843,
     841, 849, 847, 861, 865,
     762, 765, 763, 867, 768,
     772, 773]


def numbers_to_str_list(numbers):
    return ",".join([str(i) for i in numbers])


# example usage:
if __name__ == "__main__":
    print(get_testing_subgraph_polylines())
