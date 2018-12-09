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

names = ["k_Nearest_Neighbors", "SVM", # "Gaussian_Process",
         "Decision_Tree", "Random_Forest", "Neural_Net", "AdaBoost",
         "Naive_Bayes", "Logistic_Regression", 'Dummy', 'LinearReg']


feature_path = 'data/ml/graph_features.pkl'


def bit_twiddle_params(a, data, features):
    criterion=['gini', 'entropy']
    splitter=['best', 'random']
    # max_depth=[None, 100]
    # min_samples_split=[2]
    # min_samples_leaf=[1, 2, 3, 4, 5]
    max_features=[None, 'log2', 'sqrt', 'auto']
    for cr, sp, mx_features in \
            random.sample(list(itertools.product(criterion, splitter, max_features)), 16):
        options = {'criterion': cr, 'splitter': sp, 'max_features': mx_features}
        a.run(data, features, clf_options=options)
        a.to_csv()

if __name__ == "__main__":
    for n in names:
        a = algs.load_alg(n)
        data = util.load_pkl(feature_path)
        a.run(data, util.features)
        a.to_csv()
    # bit_twiddle_params(a, data, util.features)

    # param_dist = {'penalty':['l1', 'l2'], 'C':[10**i for i in range(-5, 5)]}
    # a.search(data, param_dist, ['graph_features'])
