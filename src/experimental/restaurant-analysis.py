import networkx as nx
import json
import pandas as pd

edgefile = "../../data/toronto_knn_20.csv"
restfile = "../../data/yelp_toronto.csv"
communityfile = "../../data/louvain_dict_knn_20.json"

# read in files, construct graph
edges = pd.read_csv(edgefile, ',', header = 0)    
df = pd.read_csv(restfile, sep=' ')
G = nx.from_pandas_edgelist(edges, source = 'r1', target='r2')


#community dicts
with open(communityfile, "r") as f:
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
df['degree'] = df['id'].map(lambda x: G.degree(x))

##### clustering coefficient #####
df['clustering'] = df['id'].map(lambda x: nx.clustering(G, x))

##### edge density of community #####
comm_edge_densities = {}
for idx, comm in partition.iteritems():
    H = G.subgraph(comm)
    comm_edge_densities[idx] = nx.density(H)

df['comm_edge_density'] = df['id'].map(lambda x: 0 if x not in assignments else comm_edge_densities[assignments[x]])
    
##### community size #####
df['comm_sz'] = df['id'].map(lambda x: 0 if x not in assignments else len(partition[assignments[x]]))

##### avg community rating #####
#precalculate avg community ratings
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


#predicting: review count, rating separately, review count * normalized rating? 