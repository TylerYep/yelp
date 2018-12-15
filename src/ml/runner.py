import pandas as pd
import scipy.stats
import numpy as np
import util
import itertools
from tqdm import tqdm

import os, sys
sys.path.append('ml')
import algs
from algs import Algorithm
from feature_data import DataFeatures
import random

# "Gaussian_Process", "k_Nearest_Neighbors", "Random_Forest",'Dummy',"Neural_Net","Naive_Bayes"
names = ["SVM", "Decision_Tree", "AdaBoost", "Logistic_Regression",  'LinearReg']

def bit_twiddle_params(a, data, features):
    # max_features=['log2', 'sqrt', 'auto']
    # max_depth=[5]
    # min_samples_split=[1000]
    # max_leaf_nodes=[10, 50]
    # for m, cr, mx_features, dp in random.sample(list(itertools.product(min_samples_split, max_leaf_nodes, max_features, max_depth)), 1):
    #     options = {'min_samples_split': m, 'max_leaf_nodes': cr, 'max_features': mx_features, 'max_depth': dp}
    options = {'min_samples_split': 20, 'max_features': 'log2', 'min_samples_leaf': 20}
    a.run(data, features, clf_options=options)
    a.to_csv()

if __name__ == "__main__":
    feature_path = 'data/ml/graph_features.pkl'
    x = DataFeatures(folder, True)
    for name in names:
        opts = {}
        if name == "Decision_Tree":
            opts = {'min_samples_split': 20, 'max_features': 'log2', 'min_samples_leaf': 20}
        name += "-extra"
        a = algs.load_alg(name)
        data = util.load_pkl(feature_path)

        a.run(data, util.features, clf_options=opts)
        a.to_csv()

    # folder = 'edge_rem_split_angle_norm'
    # feature_path = 'data/ml/graph_features_{}.pkl'.format(folder)
    # x = DataFeatures(folder, True)
    # for name in names:
    #     opts = {}
    #     if name == "Decision_Tree":
    #         opts = {'min_samples_split': 20, 'max_features': 'log2', 'min_samples_leaf': 20}
    #     name += "-ROUND2-angle-norm"
    #     a = algs.load_alg(name)
    #     data = util.load_pkl(feature_path)
    #
    #     a.run(data, util.features, clf_options=opts)
    #     a.to_csv()
        # param_dist = {'penalty':['l1', 'l2'], 'C':[10**i for i in range(-5, 5)]}
        # a.search(data, param_dist, ['graph_features'])
        # print(a.r.best_params)
        # bit_twiddle_params(a, data, util.features)


