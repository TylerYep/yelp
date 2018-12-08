import networkx as nx
import subprocess
import os
import pandas as pd

def general_normalize(graph, category, basegraph, nodes, rounds, norm_type):
    to_run = ['python', 'src/experimental/autoclust-investigation.py', 'graph']
    to_run.extend(['--normalize', norm_type])
    # generate category file
    cat_file = '/tmp/catgraph.csv'
    with open(cat_file) as f:
        f.write('r1,r2\n')
    nx.write_edgelist(graph, cat_file, delimiter=',')
    to_run.extend(['-f', cat_file])
    to_run.extend(['-c', category])

    # generate base graph file
    base_file = '/tmp/basegraph.csv'
    with open(cat_file) as f:
        f.write('r1,r2\n')
    nx.write_edgelist(basegraph, base_file, delimiter=',')
    to_run.extend(['-b', base_file])

    # write nodes dataframe
    nodes_file = '/tmp/points.csv'
    nodes.to_csv(nodes_file, sep=' ', quotechar='"')
    to_run.extend(['-n', nodes_file])

    # identify output directory
    out_file = '/tmp/autoclust_normalize'
    to_run.extend(['-o', autoclust_normalize])
    if rounds:
        to_run.extend(['--rounds', str(rounds)])
        expected_out_file = '/tmp/autoclust_normalize/catgraph_{}_{}.csv'.format(norm_type, rounds)
    else:
        to_run.extend(['--full'])
        expected_out_file = '/tmp/autoclust_normalize/catgraph_{}_full.csv'.format(norm_type)

    # run the thing
    subprocess.call(to_run)

    # get resulting graph
    edge = pd.read_csv(expected_out_file, ',', header=0)
    to_ret = nx.from_pandas_edge_list(edge, source='r1', target='r2', edge_attr='weight')
    return to_ret

def normalize_angle(graph, category, basegraph, nodes, rounds = None):
    '''
    Normalizes a given graph category referencing angles based on a given basegraph 
    using the distances in the given nodes dataframe.
    nodes: dataframe with id, latitude, longitude, categories
    '''
    return general_normalize(graph, category, basegraph, nodes, rounds, 'angle')

def normalize_edge(graph, category, basegraph, nodes, rounds = None):
    '''
    Normalizes a given graph category referencing edges based on a given basegraph 
    using the distances in the given nodes dataframe.
    '''
    return general_normalize(graph, category, basegraph, nodes, rounds, 'edge')
