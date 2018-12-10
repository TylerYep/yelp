import networkx as nx
import community
import pandas as pd
import json
import argparse

#python src\graph-construction\louvain.py -e data/normalized/points_delaunay_Chinese_edge_full.csv -d data/normalized/louvain_dict_edge.json -o data/normalized/louvain_edge.csv
parser = argparse.ArgumentParser(description='Detect communities with Louvain')
parser.add_argument('--edgefile', '-f', help='csv of edges', default='data/graph_calgary_knn_20.csv')
parser.add_argument('--dictfile', '-o', help='outfile', default="data/louvain_calgary_dict_knn_20.json")
args = parser.parse_args()

edge = pd.read_csv(args.edgefile, ' ', header = 0)
graph = nx.from_pandas_edgelist(edge, source = 'r1', target='r2')

partition = community.best_partition(graph) #dictionarity of node_id --> community #

# assignments = {} #dict from community # --> list of nodes in community
# for part, idx in partition.iteritems():
# 	if idx not in assignments:
# 		assignments[idx] = [part]
# 	else:
# 		assignments[idx].append(part)
# # print assignments
# with open(args.outfile, "w+") as f:
# 	for idx, assignment in tqdm(assignments.iteritems()):
# 		print len(assignment)
# 		# print assignment
# 		f.write(", ".join(assignment))
# 		f.write("\n")

with open(args.dictfile, "w+") as f:
	json.dump(partition, f)
