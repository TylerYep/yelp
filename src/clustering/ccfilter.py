import networkx as nx
import numpy as np

def filter_connected_components(graph, verbose = False):
    cc_gen = nx.connected_components(graph)
    lens, ccs = zip(*[(len(cc), cc) for cc in cc_gen])
    if verbose:
        ll = len(lens)
        slens = sorted(lens)
        print '50/95/99: {}/{}/{}'.format( \
                slens[int(0.5*ll)], slens[int(0.95*ll)], slens[int(0.99*ll)])

    nlens = np.array(lens)
    ave = np.mean(nlens)
    std = np.std(nlens)
    if verbose: 
        print "threshold: {}".format(ave + std)
    to_ret = graph.copy()
    for l, cc in zip(lens, ccs):
        if l < ave + std:
            for n in cc:
                to_ret.remove_node(n)
    return to_ret

def remove_edges_rounds(graph, rounds):
    '''
    repeatedly remove edges based on if less than ave
    '''
    vals = np.array([graph[u][v]['weight'] for u,v in graph.edges()])
    for _ in range(rounds):
        ave = np.mean(vals)
        vals = vals[np.where(vals < ave)]
    return remove_edges(graph, ave, upper=True)

def remove_edges(graph, threshold, upper):
    '''
    remove edges based on threshold. if upper is true, then threshold is
    an upper bound, else it's a lower bound
    '''
    to_ret = graph.copy()
    for u,v in graph.edges():
        if upper:
            if graph[u][v]['weight'] > threshold:
                to_ret.remove_edge(u,v)
        else:
            if graph[u][v]['weight'] < threshold:
                to_ret.remove_edge(u,v)
    return to_ret

