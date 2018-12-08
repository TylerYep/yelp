from scipy.spatial import Delaunay
import numpy as np
import networkx as nx

def delaunay(coords, nids, category_map, category = None):
    '''
    coords: array with latitude, longitude
    nids: array with corresponding node ids
    category_map: map from id to category
    category: None or a category
    '''
    if category == None:
        points = coords
    else:
        points = []
        cat_to_full = {}
        for i, point in enumerate(coords):
            if category in category_map[nids[i]]:
                cat_to_full[len(points)] = i
                points.append(point)
    x = np.array(points)
    tri = Delaunay(x, qhull_options="QJ")
    edges = set()
    for n in xrange(tri.nsimplex):
        for i in range(3):
            for j in range(i, 3):
                edge = sorted([tri.vertices[n, i], tri.vertices[n, j]])
                edges.add(tuple(edge))
    graph = nx.Graph()
    for u,v in edges:
        a = nids[cat_to_full[u]] if category else nids[u]
        b = nids[cat_to_full[v]] if category else nids[v]
        graph.add_edge(a, b)
    return graph
