import networkx as nx
import json
import os, sys
sys.path.append('src/clustering')
import knn
import evaluate
import cutoff

# sys.path.append('src/')
# from knn import knn, split
# from evaluate import get_point_info
# from cutoff import filter_connected_components

k = 8
city = "calgary"
categories = ["Coffee & Tea", "Bars", "Sandwiches", "Breakfast & Brunch", "Chinese", "Middle Eastern", "Japanese", "Pizza", "Mexican", "Mediterranean", "Korean", "Thai"]
# categories = ["Coffee & Tea"]
output_file = "data/knnsplit/graph_" + city + "_cats_uncut_8.csv"
node_file = "data/yelp_" + city + ".csv"


mapping = {}
(coords, nids, category_map, nodes) = evaluate.get_point_info(node_file)
with open(output_file.format(output_file), 'w+') as fout:
	fout.write('r1 r2 weight\n')
	end_idx = 0
	for category in categories:
		graph = knn.knn(nodes, k)
		graph = knn.split(graph, category, category_map)
		graph = cutoff.filter_connected_components(graph)
		nx.write_edgelist(graph, fout, data="weight")
		    
		
		for i, component in enumerate(nx.connected_components(graph)):
		    for node in component:
		        mapping[node] = i + end_idx
		end_idx += nx.number_connected_components(graph)

dict_file = "data/knnsplit/community_" + city + "_cats_uncut_8.json"
with open(dict_file, "w+") as f:
    json.dump(mapping, f)