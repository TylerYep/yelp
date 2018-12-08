# import pandas as pd
# import networkx as nx
# import matplotlib.pyplot as plt
# from mpl_toolkits.basemap import Basemap
# import argparse
# from collections import defaultdict
#
# colors = ['b', 'g', 'm', 'k', 'w']
#
# filename = 'data/comm.txt'
# commands = {}
# counts = defaultdict(int)
# i = 1
# with open(filename) as fh:
#     for line in fh:
#         for x in line.split():
#             if i % 2 == 0:
#                 counts[x[:-1]] += 1
#             i += 1
#
# for c in commands:
#     counts[c] += 1
# print counts
#
# for edge_file in args.edge_files:
#     edge = pd.read_csv(edge_file, ',', header = 0)
#     graph = nx.from_pandas_edgelist(edge, source = 'r1', target='r2')
#
# plt.figure(figsize = (10, 9))
#
# m = Basemap(projection='merc', \
#         llcrnrlat = rest['latitude'].min() - 0.05, \
#         urcrnrlat = rest['latitude'].max() + 0.05, \
#         llcrnrlon = rest['longitude'].min()- 0.1, \
#         urcrnrlon = rest['longitude'].max()+ 0.1, \
#         epsg = 3347)
# # For map types: http://server.arcgisonline.com/arcgis/rest/services
# # I like "World_Topo_Map" or "ESRI_Imagery_World_2D"
# m.arcgisimage(service='World_Topo_Map', xpixels = 2000, verbose= True)
#
# mx, my = m(rest['longitude'].values, rest['latitude'].values)
# pos = {}
# for i, el in enumerate(rest['id']):
#     pos[el] = (mx[i], my[i])
#
# for color, graph in zip(colors, graphs):
#     nx.draw_networkx_nodes(G = graph, pos = pos, node_list = graph.nodes(), \
#             node_color = 'r', node_size = 3)
#     nx.draw_networkx_edges(G = graph, pos = pos, edge_color = color)
# plt.show()
#
