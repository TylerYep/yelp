import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import argparse
import numpy as np
import json
import math

colors = ['b', 'g', 'm', 'k','r', 'c', 'y', 'coral', 'darkviolet']

parser = argparse.ArgumentParser(description='visualize a graph')
parser.add_argument('--rest-file', '-r', help='csv of restaurants separated by spaces', default='data/yelp_toronto.csv')
parser.add_argument('--edge-files', '-e', help='csv(s) of edges (limit of {} max)'.format(len(colors)), nargs='+', default=['data/toronto_knn_20.csv'])
parser.add_argument('--color-assignments', '-c', help='json of edges --> community #s', default=None)
parser.add_argument('--thickness', action='store_true', help='draw with thickness based on weight')
parser.add_argument('--threshold', help='threshold for edge weights', default=None, type=float)
args = parser.parse_args()

if len(args.edge_files) > len(colors):
    print 'can only currently support {} edge files'.format(len(colors))
    exit()

rest_file = args.rest_file
rest = pd.read_csv(rest_file, ' ', header = 0)
graphs = []
for edge_file in args.edge_files:
    edge = pd.read_csv(edge_file, ',', header = 0)
    if args.thickness or args.threshold:
        graph = nx.from_pandas_edgelist(edge, source = 'r1', target='r2', edge_attr='weight')
    else:
        graph = nx.from_pandas_edgelist(edge, source = 'r1', target='r2')
    graphs.append(graph)

plt.figure(figsize = (10, 9))

m = Basemap(projection='merc', \
        llcrnrlat = rest['latitude'].min() - 0.05, \
        urcrnrlat = rest['latitude'].max() + 0.05, \
        llcrnrlon = float(rest['longitude'].min())- 0.1, \
        urcrnrlon = rest['longitude'].max()+ 0.1, \
        epsg = 3347) 
# For map types: http://server.arcgisonline.com/arcgis/rest/services
# I like "World_Topo_Map" or "ESRI_Imagery_World_2D"
m.arcgisimage(service='World_Topo_Map', xpixels = 2000, verbose= True)

color_map = 'r'
if args.color_assignments:
    color_map = []
    # color_assignments = "data\louvain_dict_knn_20.json"
    with open(args.color_assignments, "r") as f:
        color_dict = json.loads(f.read())
        for node in graph.nodes():
            num = color_dict[node]
            color_map.append(colors[num % len(colors)])

mx, my = m(rest['longitude'].values, rest['latitude'].values)
pos = {}
for i, el in enumerate(rest['id']):
    pos[el] = (mx[i], my[i])

for color, graph in zip(colors, graphs):
    if args.thickness:
        u_w = [graph[u][v]['weight'] for u,v in graph.edges()]
        weights = [float(w-min(u_w))/(max(u_w)-min(u_w)) for w in u_w]
        thick = [1.0 + 10.0 * w for w in weights]
    elif args.threshold:
        thick = [1.0 if graph[u][v]['weight'] > args.threshold else 0.0 for u,v in graph.edges()]
    else:
        thick = 1.0
    # nx.draw_networkx_nodes(G = graph, pos = pos, node_list = graph.nodes(), \
    #         node_color = color_map, node_size = 10)
    nx.draw_networkx_edges(G = graph, pos = pos, edge_color = color, width = thick)
plt.show()

