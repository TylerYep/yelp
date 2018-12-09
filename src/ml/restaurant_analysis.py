import networkx as nx
import json
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def extract_features(edge_file, rest_file, louvain_dict=None):
    # read in files, construct graph
    edges = pd.read_csv(edge_file, ' ', header = 0)
    df = pd.read_csv(rest_file, sep=' ')
    G = nx.from_pandas_edgelist(edges, source = 'r1', target='r2')

    #community dicts
    # if louvain_dict:
    with open(louvain_dict, "r") as f:
        assignments = json.loads(f.read())
    partition = {}
    #translate dict from community # --> list of nodes in community
    for part, idx in assignments.iteritems():
        if idx not in partition:
            partition[idx] = [part]
        else:
            partition[idx].append(part)

    #add features to df!
    ##### degree #####
    df['degree'] = df['id'].map(lambda x: 0 if x not in assignments else G.degree(x))

    ##### clustering coefficient #####
    df['clustering'] = df['id'].map(lambda x: 0 if x not in assignments else nx.clustering(G, x))

    ##### edge density of community #####
    comm_edge_densities = {}
    for idx, comm in partition.iteritems():
        H = G.subgraph(comm)
        comm_edge_densities[idx] = nx.density(H)

    df['comm_edge_density'] = df['id'].map(lambda x: 0 if x not in assignments else comm_edge_densities[assignments[x]])

    ##### community size #####
    df['comm_sz'] = df['id'].map(lambda x: 0 if x not in assignments else len(partition[assignments[x]]))

    ##### avg community rating #####
    # precalculate avg community ratings
    comm_review_counts = {}
    for idx, comm in partition.iteritems():
        metric_sum = 0.0
        for node in comm:
            node_row = df.loc[df['id'] == node]
            metric_sum += float(node_row['review_count'])
        metric_sum /= len(comm)
        comm_review_counts[idx] = metric_sum

    df['comm_review_count'] = df['id'].map(lambda x: 0 if x not in assignments else comm_review_counts[assignments[x]])
    #predicting: review count, rating separately, review count * normalized rating?
    #now: weighting
    # df['review_count'] = df['review_count'] * df['stars'] / 5
    # df['review_count']

    cols = {'degree': df.degree, 'clustering': df.clustering, 'comm_edge_density': df.comm_edge_density,
    'comm_sz': df.comm_sz, 'comm_review_count': df.comm_review_count, 'review_count': df.review_count}
    dfeatures = pd.DataFrame(cols)
    return dfeatures

def load_graph():
    trainfeatures = extract_features("data/graph_toronto_knn_20.csv", "data/yelp_toronto.csv", "data/louvain_dict_knn_20.json")
    testfeatures = extract_features("data/graph_calgary_knn_20.csv", "data/yelp_calgary.csv", "data/louvain_calgary_dict_knn_20.json")
    trainfeatures['split'] = 0
    testfeatures['split'] = 1
    dfeatures = pd.concat([trainfeatures, testfeatures])

    # pd.to_numeric(dfeatures['review_count'], errors='coerce')
    return dfeatures
