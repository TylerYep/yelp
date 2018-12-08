import networkx as nx
import community
import pandas as pd
from tqdm import tqdm
import json

edgefile = "data/toronto_knn_20.csv"
outfile = "data/louvain_knn_20.csv"
dictfile = "data/louvain_dict_knn_20.json"
edge = pd.read_csv(edgefile, ',', header = 0)
graph = nx.from_pandas_edgelist(edge, source = 'r1', target='r2')
partition = community.best_partition(graph) #dictionary of node_id --> community #

assignments = {} # dict from community # --> list of nodes in community
for part, idx in partition.iteritems():
	if idx not in assignments:
		assignments[idx] = [part]
	else:
		assignments[idx].append(part)

with open(outfile, "w+") as f:
	for idx, assignment in tqdm(assignments.iteritems()):
		print len(assignment)
		f.write(", ".join(assignment))
		f.write("\n")

with open(dictfile, "w+") as f:
	json.dump(partition, f)