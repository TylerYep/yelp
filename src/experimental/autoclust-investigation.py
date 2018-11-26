import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os
import numpy as np
import scipy.spatial.distance as dist
import math

default_lmao = 'ripme-more'
actions = ['graph', 'analyze']
normalize_actions = ['node', 'edge', 'angle']
parser = argparse.ArgumentParser(description='visualize properties of delaunay multiplex graph')
parser.add_argument('action', nargs=1, help='what to do ({})'.format('/'.join(actions)), \
        default=actions[0])
parser.add_argument('--normalize', help='how to normalize ({})'.format('/'.join(normalize_actions)),\
        default=normalize_actions[0])
parser.add_argument('--default', help='if formatted correctly and in correct cwd, ' + \
        'auto chooses everything based on default-dir', action='store_true')
parser.add_argument('--default-dir', '-d', help='default dir name for all data', \
        default='data/fake-graphs/{}'.format(default_lmao))
parser.add_argument('--nodes', '-n', help='file of nodes')
parser.add_argument('--base', '-b', help='base delaunay graph')
parser.add_argument('--category-files', '-f', help='category delaunay graphs', nargs='+')
parser.add_argument('--categories', '-c', help='categories corresponding to files. ' + \
        'please don\'t try to include 0', nargs='+')
parser.add_argument('--output-dir', '-o', help='where to put generated graphs')
parser.add_argument('--label', '-l', help='file of labels')
args = parser.parse_args()
if args.default:
    default_dir = args.default_dir
    args.nodes = os.path.join(default_dir, 'points.csv')
    args.base = os.path.join(default_dir, 'delaunay.csv')
    args.category_files = [os.path.join(default_dir, 'categories/points_delaunay_1.csv'), \
                 os.path.join(default_dir, 'categories/points_delaunay_2.csv')]
    args.categories = ['1', '2']
    args.label = os.path.join(default_dir, 'labels.csv')
    args.output_dir = os.path.join(default_dir, 'categories')
if len(args.categories) != len(args.category_files):
    raise argparse.ArgumentError(args.categories, \
            'length of categories needs to be same as category-files')
if args.normalize not in normalize_actions:
    raise argparse.ArgumentError( \
            'normalize must be one of: [{}]'.format(','.join(normalize_actions)))

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
idmap = {row['id'] : idx for (idx, row) in nodes.iterrows()}

# get pairwise euclidean distances
points = nodes[['latitude', 'longitude']].values
matrix = dist.squareform(dist.pdist(points, metric='euclidean'))
def distance(u, v):
    return matrix[idmap[u]][idmap[v]]

# get weighted graphs of all graphs
def get_graph(edgefile):
    name = edgefile
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

def mean_edge_len(graph, node):
    edges = [graph[u][v]['distance'] for u,v in graph.edges(node)]
    return float(sum(edges)) / len(edges)

# for all nodes in a category get some stat relative to stat in base graph
# ----
# return format:
# { category : { nodes of category : stats } }
def nodewise_stats(func, exp = 2):
    basestats = {node : func(basegraph, node) for node in basegraph.nodes()}
    totalstats = {}
    for cat in graphs:
        name, graph = graphs[cat]
        catstats = {node : math.pow(float(func(graph, node)) / basestats[node], exp) \
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
def norm_edge_stats(node_func, exp = 2, zscore=False):
    basestats = {node : node_func(basegraph, node) for node in basegraph.nodes()}
    totalstats = {}
    for cat in graphs:
        totalstats[cat] = {}
        name, graph = graphs[cat]
        for node in graph.nodes():
            factor = 1.0 / float(basestats[node])
            norm_lens = {}
            for a,b in graph.edges(node):
                norm_edge_len = graph[a][b]['distance'] * factor
                norm_lens[b] = math.pow(norm_edge_len, exp)
            if zscore:
                lens = np.array(norm_lens.values())
                std = np.std(lens)
                mean = np.mean(lens)
                for b, norm_len in norm_lens.iteritems():
                    totalstats[cat][(node,b)] = (norm_len - mean) / std if std else 0.0
                    if math.isnan(totalstats[cat][(node,b)]):
                        print node, b
                        print norm_len, mean, std
                        print norm_lens
                        assert(False)
            else:
                for b, norm_len in norm_lens.iteritems():
                    totalstats[cat][(node, b)] = norm_len
    return totalstats

# get angles between each node
angle_cache = {}
def get_angle(a, b):
    if (a,b) in angle_cache:
        return angle_cache[(a,b)]
    a_loc = points[idmap[a]]
    b_loc = points[idmap[b]]
    diff = b_loc - a_loc
    to_ret = math.atan2(diff[1], diff[0])
    angle_cache[(a,b)] = to_ret
    return to_ret

# get stats per edge
# goal: can we make normalized edges based on angles?
# ----
# return format:
# { category : { nodes of category : stat } }
def angle_norm_edge_stats(exp = 2, zscore = False):
    all_base_edges = {}
    for node in basegraph.nodes():
        # get (angle, length) of base layer
        base_edges = sorted([(get_angle(a, b), basegraph[a][b]['distance']) for a,b in basegraph.edges(node)])
        assert(len(base_edges) != 0)
        # insert (first + 2pi) and (last - 2pi)
        base_edges.insert(0, (base_edges[-1][0] - 2*math.pi, base_edges[-1][1]))
        base_edges.append((base_edges[1][0] + 2*math.pi, base_edges[1][1]))
        all_base_edges[node] = base_edges

    totalstats = {}
    for cat in graphs:
        totalstats[cat] = {}
        name, graph = graphs[cat]
        for node in graph.nodes():
            base_edges = all_base_edges[node]
            norm_lens = {}
            for a,b in graph.edges(node):
                q_angle = get_angle(a, b)

                # binary search boiiis
                norm_len = None
                lo = 0
                hi = len(base_edges)-1
                while lo+1 < hi:
                    curr = (lo + hi) / 2
                    if abs(base_edges[curr][0] - q_angle) < 1e-10:
                        norm_len = graph[a][b]['distance'] * 3.0 / (base_edges[curr][1] + base_edges[curr-1][1] + base_edges[curr+1][1])
                        break
                    elif base_edges[curr][0] < q_angle:
                        lo = curr 
                    else:
                        hi = curr
                if norm_len == None:
                    norm_len = graph[a][b]['distance'] * 2.0 / (base_edges[lo][1] + base_edges[hi][1])
                norm_lens[b] = math.pow(norm_len, exp)
            if zscore:
                lens = np.array(norm_lens.values())
                std = np.std(lens)
                mean = np.mean(lens)
                for b, norm_len in norm_lens.iteritems():
                    totalstats[cat][(node,b)] = (norm_len - mean) / std if std else 0.0
                    if math.isnan(totalstats[cat][(node,b)]):
                        print node, b
                        print norm_len, mean, std
                        print norm_lens
                        assert(False)
            else:
                for b, norm_len in norm_lens.iteritems():
                    totalstats[cat][(node, b)] = norm_len
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
            uc = u in labels[cat]
            vc = v in labels[cat]
            ed = full[cat]
            if uc and vc:
                split[cat][0][(u,v)] = ed[(u,v)]
            elif uc or vc:
                split[cat][1][(u,v)] = ed[(u,v)]
            else:
                split[cat][2][(u,v)] = ed[(u,v)]
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
        plt.yscale('symlog')
        plt.legend()
        plt.show()

def edge_graph_split_categories(full):
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

def avestd_rounds(stats, rounds):
    vals = np.array(stats.values())
    for _ in range(rounds):
        ave = np.mean(vals)
        std = np.std(vals)
        vals = np.array([v for v in stats.values() if v < ave + std])
    return ave, std

def save_graph(graph, fname, weighted = True):
    with open(fname, 'wb+') as f:
        f.write('r1,r2,weight\n')
        nx.write_edgelist(graph, f, delimiter=',', data=['distance'])

if args.normalize == 'node':
    full = nodewise_stats(mean_edge_len)
    for cat in full:
        stats = full[cat]
        ave, std = avestd_rounds(stats, 2)
        name, graph = graphs[cat]
        newgraph = graph.copy()
        for node in stats:
            if stats[node] > ave + std:
                newgraph.remove_node(node)
        oname = os.path.join(os.path.dirname(name), 
                os.path.splitext(os.path.basename(name))[0] + '_' + args.normalize + '.csv')
        save_graph(newgraph, oname, weighted = False)

elif args.normalize == 'edge':
    full = norm_edge_stats(mean_edge_len)
    for cat in full:
        stats = full[cat]
        ave, std = avestd_rounds(stats, 2)
        name, graph = graphs[cat]
        newgraph = graph.copy()
        for edge in graph.edges:
            if stats[edge] > ave + std:
                newgraph.remove_edge(*edge)
        oname = os.path.join(os.path.dirname(name), \
                os.path.splitext(os.path.basename(name))[0] + '_' + args.normalize + '.csv')
        save_graph(newgraph, oname, weighted = True)

elif args.normalize == 'angle':
    full = angle_norm_edge_stats()
    for cat in full:
        stats = full[cat]
        ave, std = avestd_rounds(stats, 2)
        name, graph = graphs[cat]
        newgraph = graph.copy()
        for edge in graph.edges:
            if stats[edge] > ave + std:
                newgraph.remove_edge(*edge)
        oname = os.path.join(os.path.dirname(name), \
                os.path.splitext(os.path.basename(name))[0] + '_' + args.normalize + '.csv')
        save_graph(newgraph, oname, weighted = True)

# mx, my = (nodes['longitude'].values, nodes['latitude'].values)
# pos = {}
# for i, el in enumerate(nodes['id']):
#     pos[el] = (mx[i], my[i])
# 
# nx.draw_networkx_nodes(G = graph, pos = pos, node_list = graph.nodes(), \
#         node_color = 'r', node_size = 0)
# full_s = { tuple(sorted(k)) : math.pow(max(stats[k], stats[(k[1],k[0])]), 2) for k in stats }
# nx.draw_networkx_edges(G = graph, pos = pos, edgelist = full_s.keys(), edge_color=full_s.values(), edge_cmap=plt.cm.hot, edge_vmin=20.0, edge_vmax=100.0)
# plt.title(name)
# plt.show()
