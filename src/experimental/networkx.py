'''
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


def parse_args():
	'''
	Parses the node2vec arguments.
	'''
	parser = argparse.ArgumentParser(description="Run node2vec.")

	parser.add_argument('--input', nargs='?', default='graph/karate.edgelist',
	                    help='Input graph path')

	parser.add_argument('--output', nargs='?', default='emb/karate.emb',
	                    help='Embeddings path')

	parser.add_argument('--dimensions', type=int, default=128,
	                    help='Number of dimensions. Default is 128.')

	parser.add_argument('--walk-length', type=int, default=80,
	                    help='Length of walk per source. Default is 80.')

	parser.add_argument('--num-walks', type=int, default=10,
	                    help='Number of walks per source. Default is 10.')

	parser.add_argument('--window-size', type=int, default=10,
                    	help='Context size for optimization. Default is 10.')

	parser.add_argument('--iter', default=1, type=int,
                      help='Number of epochs in SGD')

	parser.add_argument('--workers', type=int, default=8,
	                    help='Number of parallel workers. Default is 8.')

	parser.add_argument('--p', type=float, default=1,
	                    help='Return hyperparameter. Default is 1.')

	parser.add_argument('--q', type=float, default=1,
	                    help='Inout hyperparameter. Default is 1.')

	parser.add_argument('--weighted', dest='weighted', action='store_true',
	                    help='Boolean specifying (un)weighted. Default is unweighted.')
	parser.add_argument('--unweighted', dest='unweighted', action='store_false')
	parser.set_defaults(weighted=False)

	parser.add_argument('--directed', dest='directed', action='store_true',
	                    help='Graph is (un)directed. Default is undirected.')
	parser.add_argument('--undirected', dest='undirected', action='store_false')
	parser.add_argument('--rest-file', '-r', help='csv of restaurants separated by spaces', default='data/yelp_toronto.csv')
	parser.add_argument('--edge-files', '-e', help='csv(s) of edges', nargs='+', default=['data/toronto_knn_5.csv'])
	parser.set_defaults(directed=False)

	return parser.parse_args()

def learn_embeddings(walks):
	'''
	# Learn embeddings by optimizing the Skipgram objective using SGD.
	'''
	walks = [map(str, walk) for walk in walks]
	model = Word2Vec(walks, size=args.dimensions, window=args.window_size, min_count=0, sg=1, workers=args.workers, iter=args.iter)
	model.save_word2vec_format(args.output)
	return model

def main(args):
	'''
	Pipeline for representational learning for all nodes in a graph.
	'''
	rest_file = args.rest_file
	rest = pd.read_csv(rest_file, ' ', header = 0)
	nx_G = []
	for edge_file in args.edge_files:
		edge = pd.read_csv(edge_file, ',', header = 0)
		nx_G = nx.from_pandas_edgelist(edge, source = 'r1', target='r2')
	G = node2vec.Graph(nx_G, args.directed, args.p, args.q)
	G.preprocess_transition_probs()
	walks = G.simulate_walks(args.num_walks, args.walk_length)
	model = learn_embeddings(walks)

	partition = community.best_partition(nx_G, randomize=True)
	nx.draw_spring(nx_G, with_labels=True, cmap=plt.cm.RdYlBu, node_color=list(partition))
	plt.show()



if __name__ == "__main__":
	args = parse_args()
	main(args)
