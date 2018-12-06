import snap
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import csv
import argparse
import features

parser = argparse.ArgumentParser(description='generate graph based on kNN')
parser.add_argument('--num-neighbors', '-k', help='value of k', type=int, default=20)
parser.add_argument('--radius', '-r', help='radius, if clustering by radius', type=float, default=0)
parser.add_argument('--point-file', '-f', help='file with points and categories', default='data/yelp_toronto.csv')
parser.add_argument('--output-file', '-o', help='file to output edges to. can add "{}" to record what k is', default='data/graph_toronto_{}.csv')
args = parser.parse_args()

radius_sz = args.radius
num_neighbors = args.num_neighbors
point_file = args.point_file
output_file = args.output_file

coords = []
rids = []

with open(point_file, 'r') as csvfile:
	reader = csv.reader(csvfile, delimiter=' ')
	hdr = next(reader, None) # skip header
	x_idx = hdr.index("latitude")
	y_idx = hdr.index("longitude")
	for row in reader:
		rid = row[0]
		x = row[x_idx].replace(",","")
		y = row[y_idx].replace(",","")

		coords.append([float(x), float(y)])
		rids.append(rid)

x = np.array(coords)

if radius_sz:
	print radius_sz
	nbrs = NearestNeighbors(radius=radius_sz, algorithm='auto').fit(np.array(x))
	distances, indices = nbrs.radius_neighbors(x)
else:
	nbrs = NearestNeighbors(n_neighbors=num_neighbors, algorithm='auto').fit(np.array(x))
	distances, indices = nbrs.kneighbors(x)

G = snap.TUNGraph.New()
for i in range(len(x)):
	G.AddNode(i)

if radius_sz:
	outputStr = "radius_{}".format(radius_sz)
	edgeOutput = "edgelist_" + outputStr
else:
	outputStr = "knn_{}".format(num_neighbors)
	edgeOutput = "edgelist_" + outputStr

with open(output_file.format(outputStr), 'w') as fout:
	with open(output_file.format(edgeOutput), 'w') as fout2:
		fout.write('r1,r2\n')
		for cluster in indices:
			for i in range(len(cluster)):
				for j in range(i + 1, len(cluster)):
					fout.write('{},{}\n'.format(rids[int(cluster[i])], rids[int(cluster[j])]))
					fout2.write('{},{}\n'.format(int(cluster[i]), int(cluster[j])))
					G.AddEdge(int(cluster[i]), int(cluster[j]))

features.print_features(G)
