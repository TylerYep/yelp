import networkx as nx
import os, sys
sys.path.append('src/clustering')
import knn
import evaluate
import cutoff
import json
import delaunay
import graphnormalize

city = "toronto"
categories = ["Coffee & Tea", "Bars", "Sandwiches", "Breakfast & Brunch", "Chinese",
                "Middle Eastern", "Japanese", "Pizza", "Mexican", "Mediterranean", "Korean", "Thai"]
output_file = "data/edge_rem_split_edge_norm/graph_" + city + "{}.csv"
node_file = "data/yelp_" + city + ".csv"
dict_file = "data/edge_rem_split_edge_norm/community_" + city + "{}.json"
k = 8

(coords, nids, category_map, nodes) = evaluate.get_point_info(node_file)
basegraph = delaunay.delaunay(coords, nids, category_map)

for idx, category in enumerate(categories):
    graph = delaunay.delaunay(coords, nids, category_map, category)
    # graph = graphnormalize.normalize_angle(graph, category, basegraph, nodes)
    graph = graphnormalize.normalize_edge(graph, category, basegraph, nodes)

    graph = cutoff.remove_edges_rounds(graph)
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
