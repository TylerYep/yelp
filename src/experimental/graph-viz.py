import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
from mpl_toolkits.basemap import Basemap

rest = pd.read_csv('data/yelp_toronto.csv', ' ', header = 0)

print rest.shape

# # generate edges
# edge = pd.DataFrame(columns=('r1', 'r2'))
# for i in tqdm(range(8000)):
#     while True:
#         e = rest.sample(2)['id']
#         iedge = (e.iloc[0], e.iloc[1])
#         if ((edge['r1'] == iedge[0]) & (edge['r2'] == iedge[1])).any():
#             continue
#         edge.loc[i] = iedge
#         break
# edge.to_csv('data/test_edges.csv', ',')

edge = pd.read_csv('data/test_edges.csv', ',', header = 0)

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
