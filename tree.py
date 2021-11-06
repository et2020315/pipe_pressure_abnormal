'''
File used to generate all of the pipes tree's logic.
'''

# check https://pypi.org/project/anytree/
from anytree import RenderTree
import json

'''
input: json file

output: polylines that feed into break_polylines_to_pairs 
[
    [[1, 2], [3, 4], [5, 7]],
    [[10, 11], [12, 13]]
]
'''

def read_pipe_location_json(filename):
    file = open(filename)
    locDict = json.load(file)
    feature_list = locDict["features"]
    i = 0
    pipe_loc_list = []
    for group in feature_list:
        # i += 1
        pipe_loc_list.append(group["geometry"]["paths"][0])
    return pipe_loc_list

'''
input: polylines such as:
 [
    [[1, 2], [3, 4], [5, 7]],
    [[10, 11], [12, 13]]
 ]
output:
 [
    [[1, 2], [3, 4]],
    [[3, 4], [5, 7]],
    [[10, 11], [12, 13]]
 ]
'''
def break_polylines_to_pairs(polylines):
    total = []
    for item in polylines:
        if len(item) <= 1:
            continue
        elif len(item) == 2:
            total.append(item)
        else:
            for i in range(len(item) - 1):
                group = []
                group.append(item[i])
                group.append(item[i + 1])
                total.append(group)
    return total


'''
input:  
 [
    [[1, 2], [3, 4]],
    [[3, 4], [5, 7]],
    [[10, 11], [12, 13]]
 ],
 [
    [4, 4],
    [2, 7],
    [1, 4]
 ]
 
 output:
 RenderTree
 * with water_plant as the root node
 * with buildings as leafs
'''
def lines_to_tree(edges, building_locations, water_plant) -> RenderTree:
    pass



domestic_hot_name = "data/domesticHotPipe.json"
domestic_cold_name = "data/domesticColdPipe.json"
domestic_hot_dim = read_pipe_location_json(domestic_hot_name)
domestic_hot_break = break_polylines_to_pairs(domestic_hot_dim)

for item in domestic_hot_break:
    print("\n")
    print(item)