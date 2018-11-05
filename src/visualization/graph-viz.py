import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import argparse

parser = argparse.ArgumentParser(description='visualize a graph')
parser.add_argument('--rest-file', '-r', help='csv of restaurants separated by spaces', default='data/yelp_toronto.csv')
parser.add_argument('--edge-file', '-e', help='csv of edges separated by commas', default='data/toronto_knn_5.csv')
args = parser.parse_args()

rest_file = args.rest_file
edge_file = args.edge_file

rest = pd.read_csv(rest_file, ' ', header = 0)
edge = pd.read_csv(edge_file, ',', header = 0)

graph = nx.from_pandas_edgelist(edge, source = 'r1', target='r2')

plt.figure(figsize = (10, 9))

m = Basemap(projection='merc', \
        llcrnrlat = rest['latitude'].min() - 0.05, \
        urcrnrlat = rest['latitude'].max() + 0.05, \
        llcrnrlon = rest['longitude'].min()- 0.1, \
        urcrnrlon = rest['longitude'].max()+ 0.1, \
        epsg = 3347) 
# For map types: http://server.arcgisonline.com/arcgis/rest/services
# I like "World_Topo_Map" or "ESRI_Imagery_World_2D"
m.arcgisimage(service='World_Topo_Map', xpixels = 2000, verbose= True)

mx, my = m(rest['longitude'].values, rest['latitude'].values)
pos = {}
for i, el in enumerate(rest['id']):
    pos[el] = (mx[i], my[i])

nx.draw_networkx_nodes(G = graph, pos = pos, node_list = graph.nodes(), \
        node_color = 'r', node_size = 3)
nx.draw_networkx_edges(G = graph, pos = pos, edge_color = 'b')
plt.show()
