import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import networkx as nx

def knn(nodes, k):
    '''
    given nodes dataframe and k, return knn
    nodes: dataframe with latitude, longitude, id
    '''
    x = nodes[['latitude','longitude']]
    nids = nodes[['id']]
    to_nids = {k : v['id'] for k, v in nids.to_dict('index').iteritems()}
    nbrs = NearestNeighbors(n_neighbors=k, algorithm='auto').fit(x)
    A = nbrs.kneighbors_graph(x).toarray()
    undirA = ((A == 1) | (A.T == 1)).astype(int)
    graph = nx.convert_matrix.from_numpy_matrix(undirA)
    graph.remove_edges_from(graph.selfloop_edges())
    graph.remove_nodes_from(list(nx.isolates(graph)))
    nx.relabel_nodes(graph, to_nids, copy=False)
    return graph

def split(graph, category, category_map):
    '''
    split graph based on node attributes
    '''
    to_ret = graph.copy()
    for u,v in graph.edges():
        if category not in category_map[u] or category not in category_map[v]:
            to_ret.remove_edge(u,v)
    to_ret.remove_nodes_from(list(nx.isolates(to_ret)))
    return to_ret

if __name__ == '__main__':
    points = pd.read_csv('data/yelp/points.csv', delimiter=' ', quotechar='"')
    print len(knn(points, 3).edges())
    edge = pd.read_csv('data/yelp/edges-knn_3.csv', ',', header=0)
    other_graph = nx.from_pandas_edgelist(edge, source='r1', target='r2')
    other_graph.remove_edges_from(other_graph.selfloop_edges())
    print len(other_graph.edges())
