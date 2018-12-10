import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import argparse
import os

colors = ['b', 'g', 'm', 'k', 'w']

parser = argparse.ArgumentParser(description='visualize a graph')
parser.add_argument('--node-file', '-n', help='csv of nodes separated by spaces', default='data/fake-graphs/1/points.csv')
parser.add_argument('--edge-files', '-e', help='csv(s) of edges (limit of {} max)'.format(len(colors)), nargs='+', default=['data/fake-graphs/1/categories/edges-20_0.csv'])
parser.add_argument('--thickness', help='thickness', default=None, action='store_true')
parser.add_argument('--threshold', help='threshold for edge weights', default=None, type=float)
parser.add_argument('--upper-bound', help='threshold is upperbound', action='store_true')
args = parser.parse_args()

if len(args.edge_files) > len(colors):
    print 'can only currently support {} edge files'.format(len(colors))
    exit()

rest_file = args.node_file
rest = pd.read_csv(rest_file, ' ', header = 0)

graphs = []
for edge_file in args.edge_files:
    edge = pd.read_csv(edge_file, ',', header = 0)
    if args.thickness or args.threshold:
        graph = nx.from_pandas_edgelist(edge, source = 'r1', target='r2', edge_attr='weight')
    else:
        graph = nx.from_pandas_edgelist(edge, source = 'r1', target='r2')
    graphs.append(graph)

plt.figure(figsize = (20, 18))

mx, my = (rest['latitude'].values, rest['longitude'].values)
pos = {}
for i, el in enumerate(rest['id']):
    pos[el] = (mx[i], my[i])

for color, graph, efile in zip(colors, graphs, args.edge_files):
    if args.thickness:
        unnormed_weights = [graph[u][v]['weight'] for u,v in graph.edges()]
        weights = [ float(w-min(unnormed_weights))/(max(unnormed_weights)-min(unnormed_weights)) for w in unnormed_weights ]
        thick = [1.0 + 10.0 * w for w in weights]
    elif args.threshold:
        if args.upper_bound:
            thick = [1.0 if graph[u][v]['weight'] < args.threshold else 0.0 for u,v in graph.edges()]
        else:
            thick = [1.0 if graph[u][v]['weight'] > args.threshold else 0.0 for u,v in graph.edges()]
    else:
        thick = 1.0
    nx.draw_networkx_nodes(G = graph, pos = pos, node_list = graph.nodes(), \
            node_color = 'r', node_size = 0)
    nx.draw_networkx_edges(G = graph, pos = pos, edge_color = color, label=os.path.basename(efile), width=thick)
# plt.legend()
plt.show()
