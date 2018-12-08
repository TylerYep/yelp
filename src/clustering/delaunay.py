from scipy.spatial import Delaunay

def delaunay(nodes, category_map, category = None):
    '''
    nodes: dataframe with latitude, longitude, id
    category_map: map from id to category
    category: None or a category
    '''
    coords = nodes[['latitude', 'longitude']]
    nids = nodes[['id']]
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
    for e in edges:
        graph.add_edge(e[0], e[1])
    return graph
