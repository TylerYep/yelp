import snap
import matplotlib.pyplot as plt
from collections import defaultdict

def print_features(G):
    # nodes = G.GetNodes()
    # edges = G.GetEdges()
    # print('Nodes', nodes)
    # print('Edges', edges)
    # print('Verify no self-edges', snap.CntSelfEdges(G))
    # print('Clustering Coeff', snap.GetClustCf(G))
    # HITS(G)
    # plotDegDist(G)
    # print('Modularity', modularity(G, 40, edges))
    community_detection(G)

def community_detection(G):
    '''
    See snap docs for details.
    '''
    CmtyV = snap.TCnComV()
    # Only for large networks - I got 3000 node communities on a 9000 node graph...
    # modularity = snap.CommunityCNM(G, CmtyV)
    modularity = snap.CommunityGirvanNewman(G, CmtyV)
    for Cmty in CmtyV:
        print "Community size: ", len(Cmty)
    print "The modularity of the network is %f" % modularity

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
