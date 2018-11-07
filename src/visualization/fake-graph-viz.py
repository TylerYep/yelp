import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import argparse

colors = ['b', 'g', 'm', 'k', 'w']

parser = argparse.ArgumentParser(description='visualize a graph')
parser.add_argument('--node-file', '-n', help='csv of nodes separated by spaces', default='data/fake-graphs/1/points.csv')
parser.add_argument('--edge-files', '-e', help='csv(s) of edges (limit of {} max)'.format(len(colors)), nargs='+', default=['data/fake-graphs/1/categories/edges-20_0.csv'])
args = parser.parse_args()

if len(args.edge_files) > len(colors):
    print 'can only currently support {} edge files'.format(len(colors))
    exit()

rest_file = args.node_file
rest = pd.read_csv(rest_file, ' ', header = 0)

graphs = []
for edge_file in args.edge_files:
    edge = pd.read_csv(edge_file, ',', header = 0)
    graph = nx.from_pandas_edgelist(edge, source = 'r1', target='r2')
    graphs.append(graph)

plt.figure(figsize = (20, 18))

mx, my = (rest['longitude'].values, rest['latitude'].values)
pos = {}
for i, el in enumerate(rest['id']):
    pos[el] = (mx[i], my[i])

for color, graph in zip(colors, graphs):
    nx.draw_networkx_nodes(G = graph, pos = pos, node_list = graph.nodes(), \
            node_color = 'r', node_size = 0)
    nx.draw_networkx_edges(G = graph, pos = pos, edge_color = color)
plt.show()
