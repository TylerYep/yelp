import snap
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import csv
import argparse

parser = argparse.ArgumentParser(description='generate graph based on kNN')
parser.add_argument('--num-neighbors', '-k', help='value of k', type=int, default=20)
parser.add_argument('--point-file', '-f', help='file with points and categories', default='data/yelp_toronto.csv')
parser.add_argument('--output-file', '-o', help='file to output edges to. can add "{}" to record what k is', default='data/toronto_knn_{}.csv')
args = parser.parse_args()

num_neighbors = args.num_neighbors
point_file = args.point_file
output_file = args.output_file

coords = []
rids = []

with open(point_file, 'r') as csvfile:
	reader = csv.reader(csvfile, delimiter=' ')
	next(reader, None) # skip header
	for row in reader:
		rid = row[0]
		x = row[1].replace(",","")
		y = row[2].replace(",","")
	
		coords.append([float(x), float(y)])
		rids.append(rid)

x = np.array(coords)
nbrs = NearestNeighbors(n_neighbors=num_neighbors, algorithm='auto').fit(np.array(x))
distances, indices = nbrs.kneighbors(x)

G = snap.TUNGraph.New()
for i in range(len(x)):
	G.AddNode(i)

with open(output_file.format(num_neighbors), 'w') as fout:
	fout.write('r1,r2\n')
	for cluster in indices:
		for i in range(len(cluster)):
			for j in range(i + 1, len(cluster)):
				fout.write('{},{}\n'.format(rids[int(cluster[i])], rids[int(cluster[j])]))
				G.AddEdge(int(cluster[i]), int(cluster[j]))

print G.GetNodes()
print G.GetEdges()
