import snap
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import csv

coords = []

with open('data/yelp_toronto.csv', 'r') as csvfile:
	reader = csv.reader(csvfile, delimiter=' ')
	for row in reader:
		x = row[1].replace(",","")
		y = row[2].replace(",","")
	
		coords.append([float(x), float(y)])

x = np.array(coords)
nbrs = NearestNeighbors(n_neighbors=5, algorithm='auto').fit(np.array(x))
distances, indices = nbrs.kneighbors(x)

G = snap.TUNGraph.New()
for i in range(len(x)):
	G.AddNode(i)

for cluster in indices:
	for i in range(len(cluster)):
		for j in range(i + 1, len(cluster)):
			G.AddEdge(int(cluster[i]), int(cluster[j]))

print G.GetNodes()
print G.GetEdges()
