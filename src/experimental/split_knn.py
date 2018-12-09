import networkx as nx
import os, sys
sys.path.append('src/clustering')
import knn
import evaluate
import cutoff
# from knn import knn, split
# from evaluate import get_point_info
# from cutoff import filter_connected_components

output_file = "data/knnsplit/graph_toronto_8.csv"
node_file = "data/yelp_toronto.csv"
k = 8


(coords, nids, category_map, nodes) = evaluate.get_point_info(node_file)
graph = knn.knn(nodes, k)
graph = knn.split(graph, "Chinese", category_map)
graph = cutoff.filter_connected_components(graph)

with open(output_file.format(output_file), 'wb+') as fout:
    fout.write('r1 r2 weight\n')
    nx.write_edgelist(graph, fout, data="weight")