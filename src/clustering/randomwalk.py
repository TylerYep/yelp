'''
Code adapted from:
Reference implementation of node2vec.

Author: Aditya Grover

For more details, refer to the paper:
node2vec: Scalable Feature Learning for Networks
Aditya Grover and Jure Leskovec
Knowledge Discovery and Data Mining (KDD), 2016
'''
import argparse
import numpy as np
import networkx as nx
import node2vec
from gensim.models import Word2Vec
import matplotlib.pyplot as plt
import community
import pandas as pd
import collections
import math
from tqdm import tqdm

def parse_args():
    '''
    Parses the node2vec arguments.
    '''
    parser = argparse.ArgumentParser(description="Run node2vec.")

    parser.add_argument('--input', nargs='?', default='graph/karate.edgelist',
                        help='Input graph path')

    parser.add_argument('--walk-length', type=int, default=3,
                        help='Length of walk per source. Default is 80.')

    parser.add_argument('--num-walks', type=int, default=10,
                        help='Number of walks per source. Default is 10.')

    parser.add_argument('--workers', type=int, default=8,
                        help='Number of parallel workers. Default is 8.')

    parser.add_argument('--p', type=float, default=1,
                        help='Return hyperparameter. Default is 1.')

    parser.add_argument('--q', type=float, default=1,
                        help='Inout hyperparameter. Default is 1.')

    parser.add_argument('--directed', dest='directed', action='store_true',
                        help='Graph is (un)directed. Default is undirected.')
    parser.add_argument('--undirected', dest='undirected', action='store_false')
    parser.add_argument('--rest-file', '-r', help='csv of restaurants separated by spaces', default='data/yelp_toronto.csv')
    parser.add_argument('--edge-file', '-e', help='csv(s) of edges', default='data/toronto_knn_5.csv')
    parser.set_defaults(directed=False)

    return parser.parse_args()

def dot(a, b):
    s = 0.0
    m, n = (a, b) if len(a) < len(b) else (b, a)
    for k in m:
        if k in n:
            s += float(m[k]) * n[k]
    return s

def cossim(a, b):
    return dot(a,b) / math.sqrt(dot(a,a) * dot(b,b))

def calc_pvisit(walks):
    probs = {}
    for walk in walks:
        start = walk[0]
        if start not in probs:
            probs[start] = {1:collections.defaultdict(int), 
                    2:collections.defaultdict(int), 
                    3:collections.defaultdict(int)}
        for i, n in enumerate(walk[1:]):
            probs[start][i+1][n] += 1
    # normalize
    p_visit = {}
    for start in probs:
        p_visit[start] = collections.defaultdict(float)
        for step in probs[start]:
            counts = probs[start][step]
            norm_factor = sum(counts.values())
            for n, count in counts.iteritems():
                p_visit[start][n] += float(count) / norm_factor
    return p_visit

def ns(nx_G, num_walks=100, walk_length=3):
    G = node2vec.Graph(nx_G, False, 1, 1)
    G.preprocess_transition_probs()
    walks = G.simulate_walks(num_walks, walk_length, False)

    p_visit = calc_pvisit(walks)
    graph = nx_G.copy()
    for u,v in graph.edges():
        graph[u][v]['weight'] = cossim(p_visit[u], p_visit[v])
    return graph

def calc_ce(walks):
    rt_counts = collections.defaultdict(int)
    walk_counts = collections.defaultdict(int)
    for walk in walks:
        start = walk[0]
        walk_counts[start] += 1
        counts = collections.defaultdict(int)
        for e in walk[1:]:
            if e == start:
                break
            counts[e] += 1
        for k, v in counts.iteritems():
            if v == 1:
                rt_counts[(start, k)] += 1
    probs = collections.defaultdict(float)
    for k in rt_counts:
        probs[k] = float(rt_counts[k]) / walk_counts[k[0]]
    return probs

def ce(nx_G, k=3, num_walks=10, walk_length=3):
    newgraph = nx_G.copy()
    for u,v in tqdm(nx_G.edges()):
        s_u = set(nx.single_source_shortest_path_length(nx_G, u, cutoff=k).keys())
        s_v = set(nx.single_source_shortest_path_length(nx_G, u, cutoff=k).keys())
        sg = node2vec.Graph(nx_G.subgraph(s_u.union(s_v)), False, 1, 1)
        sg.preprocess_transition_probs()
        walks = sg.simulate_walks(num_walks, walk_length, False)
        probs = calc_ce(walks)
        newgraph[u][v]['weight'] = newgraph[v][u]['weight'] = 0.5 * (probs[(u,v)] + probs[(v,u)])
    return newgraph

def invert_graph_probs(graph):
    graph = graph.copy()
    for u,v in graph.edges():
        graph[u][v]['weight'] = 1./(graph[u][v]['weight']+1)
    return graph

def main(args):
    '''
    Pipeline for representational learning for all nodes in a graph.
    '''
    rest_file = args.rest_file
    edge_file = args.edge_file
    rest = pd.read_csv(rest_file, ' ', header = 0)
    edge = pd.read_csv(edge_file, ',', header = 0)
    nx_G = nx.convert_matrix.from_pandas_edgelist(edge, source = 'r1', target='r2', edge_attr='weight')
    graph = ce(ce(ce(nx_G, 3), 3), 3)
    with open('test', 'wb+') as f:
        f.write('r1,r2,weight\n')
        nx.write_edgelist(graph, f, delimiter=',', data=['weight'])

if __name__ == "__main__":
    args = parse_args()
    main(args)
