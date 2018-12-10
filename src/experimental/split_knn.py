import networkx as nx
import os, sys
sys.path.append('src/clustering')
import knn
import evaluate
import cutoff
import json

cities = ["toronto", "calgary", "montreal"]
categories = ["Coffee & Tea", "Bars", "Sandwiches", "Breakfast & Brunch", "Chinese",
				"Middle Eastern", "Japanese", "Pizza", "Mexican", "Mediterranean", "Korean", "Thai"]

for city in cities:
	output_file = "data/knnsplit/graph_" + city + "{}_8.csv"
	node_file = "data/yelp_" + city + ".csv"
	dict_file = "data/knnsplit/community_" + city + "{}_8.json"
	k = 8

	(coords, nids, category_map, nodes) = evaluate.get_point_info(node_file)

	for idx, category in enumerate(categories):
		graph = knn.knn(nodes, k)
		graph = knn.split(graph, category, category_map)
		# graph = cutoff.filter_connected_components(graph)

		with open(output_file.format(idx), 'w+') as fout:
		    fout.write('r1 r2 weight\n')
		    nx.write_edgelist(graph, fout, data="weight")

		mapping = {}
		for i, component in enumerate(nx.connected_components(graph)):
		    for node in component:
		        mapping[node] = i

		with open(dict_file.format(idx), "w+") as f:
		    json.dump(mapping, f)
