import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import networkx as nx

def knn(nodes, k):
    '''
    given nodes dataframe and k, return knn
    '''
    x = nodes[['latitude','longitude']]
    nids = nodes[['id']]
    to_nids = {k : v['id'] for k, v in nids.to_dict('index').iteritems()}
    nbrs = NearestNeighbors(n_neighbors=k, algorithm='auto').fit(x)
    A = nbrs.kneighbors_graph(x).toarray()
    print A.shape
    undirA = ((A == 1) | (A.T == 1)).astype(int)
    print undirA
    graph = nx.convert_matrix.from_numpy_matrix(undirA)
    graph.remove_edges_from(graph.selfloop_edges())
    nx.relabel_nodes(graph, to_nids, copy=False)
    return graph

if __name__ == '__main__':
    points = pd.read_csv('data/yelp/points.csv', delimiter=' ', quotechar='"')
    print len(knn(points, 3).edges())
    edge = pd.read_csv('data/yelp/edges-knn_3.csv', ',', header=0)
    other_graph = nx.from_pandas_edgelist(edge, source='r1', target='r2')
    other_graph.remove_edges_from(other_graph.selfloop_edges())
    print len(other_graph.edges())
