import community
import numpy as np
import networkx as nx

def louvain(graph):
    '''
    louvain on given graph
    if directed, make sure edge attribute is 'weight'
    '''
    part = community.best_partition(graph) # dict node_id -> community #
    communities = {}
    for node, comm in part.iteritems():
        if comm not in communities:
            communities[comm] = set()
        communities[comm].add(node)
    return list(communities.values())

def get_edge_density(graph, nodeset):
    return nx.density(graph.subgraph(nodeset))

def get_ave_edge_len(graph, nodeset):
    sg = graph.subgraph(nodeset)
    lens = [sg[u][v]['weight'] for u,v in sg.edges()]
    return float(sum(lens))/len(lens)

def filter_communities(graph, communities, filter_on='edge_density', verbose=False):
    '''
    filter communities either by edge density or average edge length
    '''
    communities = [comm for comm in communities if len(comm) > 1] # remove isolated nodes
    if filter_on == 'edge_density':
        func = get_edge_density
        should_rem = lambda a,b: a < b
    elif filter_on == 'edge_length':
        func = get_ave_edge_len
        should_rem = lambda a,b: a > b
    densities = np.asarray([func(graph, comm) for comm in communities])
    if verbose:
        sdens = sorted(densities)
        ldens = len(densities)
        print 'num communities: {}'.format(ldens)
        print '50/95/99: {:.4f}/{:.4f}/{:.4f}'.format( \
                sdens[int(0.5*ldens)], sdens[int(0.95*ldens)], sdens[int(0.99*ldens)])
    ave = np.mean(densities)
    std = np.std(densities)
    threshold = ave
    if verbose:
        print "threshold: {}".format(threshold)
    to_ret = graph.copy()
    for density, community in zip(densities, communities):
        if should_rem(density, threshold):
            for n in community:
                to_ret.remove_node(n)
    return to_ret
