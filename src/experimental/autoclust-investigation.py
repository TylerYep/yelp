import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os
from scipy.spatial.distance import pdist, squareform

default_lmao = 'simple' # holy jank
parser = argparse.ArgumentParser(description='visualize properties of delaunay multiplex graph')
default_dir = 'data/fake-graphs/{}'.format(default_lmao)
parser.add_argument('--nodes', '-n', help='file of nodes', default=default_dir + '/points.csv')
parser.add_argument('--base', '-b', help='base delaunay graph', default=default_dir + '/delaunay.csv')
parser.add_argument('--category-files', '-f', help='category delaunay graphs', nargs='+', \
        default=[default_dir + '/categories/points_delaunay_1.csv', \
                 default_dir + '/categories/points_delaunay_2.csv'])
parser.add_argument('--categories', '-c', help='categories corresponding to files', nargs='+', \
        default=['1', '2'])
parser.add_argument('--label', '-l', help='file of labels', default=default_dir + '/labels.csv')
args = parser.parse_args()
if len(args.categories) != len(args.category_files):
    raise argparse.ArgumentError(args.categories, 'length of categories needs to be same as category-files')

# read {label : set(nodes w/ that label)}
labelfile = args.label
labels = {cat : set() for cat in args.categories}
with open(labelfile, 'r') as f:
    for l in f:
        blah = l.split()
        k = int(blah[0])
        v = blah[1]
        if v in labels:
            labels[v].add(k)
nodefile = args.nodes
nodes = pd.read_csv(nodefile, ' ', header=0)

# catlabel format:
# { category : [
#       set( nodes of category in high density ),
#       set( nodes of category not in high density )
# ] }
catlist = nodes['categories'].str.split(', ').tolist()
idmap = {row['id'] : idx for (idx, row) in nodes.iterrows()}
idxmap = {v : k for k, v in idmap.iteritems()}
catlabels = {}
for cat in labels:
    catlabels[cat] = [None, None]
    # all points of given category
    allcatlabels = set([idxmap[i] for i, x in enumerate(catlist) \
            if isinstance(x, (list,)) and cat in x])
    assert(not (labels[cat] - allcatlabels))
    # all points of given category in high density
    catlabels[cat][0] = labels[cat]
    # all points of given category not in high density
    catlabels[cat][1] = allcatlabels - labels[cat]

# get pairwise euclidean distances
matrix = squareform(pdist(nodes[['latitude', 'longitude']].values, metric='euclidean'))
def distance(u, v):
    return matrix[idmap[u]][idmap[v]]

# get weighted graphs of all graphs
def get_graph(edgefile):
    name = os.path.basename(edgefile)
    edges = pd.read_csv(edgefile, ',', header=0)
    graph = nx.from_pandas_edgelist(edges, source='r1', target='r2')
    graph.remove_edges_from(graph.selfloop_edges())
    for u, v in graph.edges():
        graph[u][v]['distance'] = distance(u, v)
    return name, graph

basename, basegraph = get_graph(args.base)
graphs = {}
for cat, catfile in zip(args.categories, args.category_files):
    name, graph = get_graph(catfile)
    graphs[cat] = (name, graph)

# for all nodes in a category get some stat relative to stat in base graph
# ----
# return format:
# { category : { nodes of category : stats } }
def nodewise_stats(func):
    basestats = {node : func(basegraph, node) for node in basegraph.nodes()}
    totalstats = {}
    for cat in graphs:
        name, graph = graphs[cat]
        catstats = {node : (float(func(graph, node)) / basestats[node]) \
                for node in graph.nodes()}
        totalstats[cat] = catstats
    return totalstats

# split totalstats based on labels
# ----
# return format:
# { category : [ 
#    { nodes of category in high-density : stats }, 
#    { nodes of category not in high-density : stats } 
# ] }
def split_node_stats(full):
    split = {}
    for cat in full:
        split[cat] = [{}, {}]
        for node in full[cat]:
            if node in labels[cat]:
                split[cat][0][node] = full[cat][node]
            else:
                split[cat][1][node] = full[cat][node]
    return split

# get stats per edge
# goal: what is the threshold for Long_Edges? (edges not between clusters)
# ----
# return format:
# { category : { nodes of category : stat } }
def norm_edge_stats(node_func):
    basestats = {node : node_func(basegraph, node) for node in basegraph.nodes()}
    totalstats = {}
    for cat in graphs:
        totalstats[cat] = {}
        name, graph = graphs[cat]
        for node in graph.nodes():
            factor = float(basestats[node]) / node_func(graph, node)
            for a,b in graph.edges(node):
                norm_edge_len = graph[a][b]['distance'] * factor
                totalstats[cat][(a,b)] = norm_edge_len
    return totalstats

# split totalstats based on labels
# ----
# return format:
# { category : [
#       { edges in high-density : stats },
#       { edges between high-density and not : stats },
#       { edges not in high-density : stats }
# ] }
def split_edge_stats(full):
    split = {}
    for cat in graphs:
        split[cat] = [{}, {}, {}]
        name, graph = graphs[cat]
        for u,v in graph.edges():
            cluster = catlabels[cat][0]
            uc = u in cluster
            vc = v in cluster
            ed = full[cat]
            if uc and vc:
                split[cat][0][(u,v)] = ed[(u,v)]
                split[cat][0][(v,u)] = ed[(v,u)]
            elif uc or vc:
                split[cat][1][(u,v)] = ed[(u,v)]
                split[cat][1][(v,u)] = ed[(v,u)]
            else:
                split[cat][2][(u,v)] = ed[(u,v)]
                split[cat][2][(v,u)] = ed[(v,u)]
    return split

def node_graph_split_categories(func):
    full = nodewise_stats(func)
    split = split_node_stats(full)
    for cat in split:
        hd = split[cat][0].values()
        no = split[cat][1].values()
        tot = hd + no
        ave = sum(tot) / len(tot)
        plt.hist(hd, 50, facecolor='g', alpha=0.5, label='high-density')
        plt.hist(no, 50, facecolor='r', alpha=0.5, label='no high-density')
        plt.axvline(x = ave)
        plt.title('category: {}'.format(cat))
        plt.legend()
        plt.show()

def edge_graph_split_categories(func):
    full = norm_edge_stats(func)
    split = split_edge_stats(full)
    for cat in split:
        both = split[cat][0].values()
        one = split[cat][1].values()
        none = split[cat][2].values()
        plt.hist(both, 50, facecolor='g', alpha=0.5, label='both')
        plt.hist(one, 50, facecolor='r', alpha=0.5, label='one')
        plt.hist(none, 50, facecolor='b', alpha=0.5, label='none')
        plt.title('category: {}'.format(cat))
        plt.yscale('symlog')
        plt.legend()
        plt.show()

# ---- mean edge length investigation ----
def mean_edge_len(graph, node):
    edges = [graph[u][v]['distance'] for u,v in graph.edges(node)]
    return float(sum(edges)) / len(edges)
edge_graph_split_categories(mean_edge_len)
# node_graph_split_categories(mean_edge_len)
