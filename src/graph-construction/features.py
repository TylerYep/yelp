import snap
import matplotlib.pyplot as plt
from collections import defaultdict
import networkx as nx
import pandas as pd
from tqdm import tqdm
import json

def print_features(G):
    # analyze_graph(G)
    nodes = G.GetNodes()
    # edges = G.GetEdges()
    # print('Nodes', nodes)
    # print('Edges', edges)
    # print('Verify no self-edges', snap.CntSelfEdges(G))
    # print('Clustering Coeff', snap.GetClustCf(G))
    # # HITS(G)
    # plotDegDist(G)
    # print('Modularity', modularity(G, 40, edges))

def analyze_graph(G):
    WCC = snap.GetMxWcc(G)
    SCC = snap.GetMxScc(G)

    id = SCC.GetRndNId()
    out_tree = snap.GetBfsTree(G, id, True, False)
    in_tree = snap.GetBfsTree(G, id, False, True)

    G_size = G.GetNodes()
    SCC_size = SCC.GetNodes()
    WCC_size = WCC.GetNodes()
    DISCONNECTED_size = G_size - WCC_size
    in_size = in_tree.GetNodes() - SCC_size
    out_size = out_tree.GetNodes() - SCC_size
    Tendril_size = G_size - SCC_size - DISCONNECTED_size - in_size - out_size

    print 'Total Graph Size: %d' % G_size
    print 'SCC Size: %d' % SCC_size
    print 'WCC Size: %d' % WCC_size
    print 'IN Size: %d' % in_size
    print 'OUT Size: %d' % out_size
    print 'DISCONNECTED Size: %d' % DISCONNECTED_size
    print 'Tendril tube size (remaining): %d' % Tendril_size
    print()

def community_detection(G):
    '''
    See snap docs for details.
    '''
    # Only for large networks - I got 3000 node communities on a 9000 node graph...
    # modularity = snap.CommunityCNM(G, CmtyV)

    edgefile = "data/toronto_knn_20.csv"
    outfile = "data/CGN_knn_20.csv"
    dictfile = "data/CGN_dict_knn_20.json"
    edge = pd.read_csv(edgefile, ',', header = 0)
    graph = nx.from_pandas_edgelist(edge, source = 'r1', target='r2')
    CmtyV = snap.TCnComV()
    modularity = snap.CommunityGirvanNewman(G, CmtyV)

    community_id = 0
    comm_dict = dict()
    for Cmty in CmtyV:
        comm_dict[community_id] = []
        for c in Cmty:
            comm_dict[community_id].append(c)
        community_id += 1

    with open(outfile, "w+") as f:
    	for idx, assignment in tqdm(assignments.iteritems()):
    		print len(assignment)
    		f.write(", ".join(assignment))
    		f.write("\n")

    with open(dictfile, "w+") as f:
    	json.dump(partition, f)




def modularity(G, id, edges):
    Nodes = snap.TIntV()
    best = 0.0
    for n_id in range(60, 150, 2):
        v = G.GetNI(n_id)
        for neighbor in [v.GetNbrNId(neighbor) for neighbor in range(v.GetDeg())]:
            Nodes.Add(neighbor)
        mod = snap.GetModularity(G, Nodes, edges)
        if mod > best:
            best = mod
    return mod


def HITS(G):
    NIdHubH = snap.TIntFltH()
    NIdAuthH = snap.TIntFltH()
    snap.GetHits(G, NIdHubH, NIdAuthH)
    max = 0.0
    for item in NIdHubH:
        if NIdHubH[item] > max:
            max = NIdHubH[item]
            print item, NIdHubH[item]

    max = 0.0
    for item in NIdAuthH:
        if NIdAuthH[item] > max:
            max = NIdAuthH[item]
            print item, NIdAuthH[item]

def plotDegDist(G):
    """
    Function to plot the distributions of two given graphs on a log-log scale.
    """
    ###########################################################################
    X, Y = [], []
    histogram = defaultdict(int)
    for n in G.Nodes():
        histogram[n.GetDeg()] += 1
    for k in sorted(histogram.keys()):
        X.append(k)
        Y.append(histogram[k])
    print(sorted(histogram.keys(), reverse=True)[:5])
    plt.scatter(X, Y, s=4)
    # plt.yscale('log')
    # plt.xscale('log')
    plt.xlabel('Node Degree')
    plt.ylabel('Proportion of Nodes with a Given Degree')
    plt.title('Degree Distribution')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    # edge = pd.read_csv('data/toronto_knn_5.csv', ',', header = 0)
    # G = nx.from_pandas_edgelist(edge, source = 'r1', target='r2')

    G = snap.LoadEdgeList(snap.PUNGraph, 'data/graph_toronto_edgelist_knn_20.csv', 0, 1, ',')
    print(G.GetNodes())
    community_detection(G)
