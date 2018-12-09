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
"""
names = ["k_Nearest_Neighbors", "SVM", "Gaussian_Process",
         "Decision_Tree", "Random_Forest", "Neural_Net", "AdaBoost",
         "Naive_Bayes", "Logistic_Regression", 'Dummy', 'LinearReg']
"""

feature_path = 'data/ml/graph_features.pkl'


def bit_twiddle_params(a, data, features):
    a.run(data, features)
    a.to_csv()

    # for es in {50, 100, 150, 200}:
    #     for eta in tqdm(range(1, 11)):
    #         # options = {'n_estimators': es, 'learning_rate': eta * 0.1}
    #         a.run(data, features)#, clf_options=options)
    #         a.to_csv()

if __name__ == "__main__":
    a = algs.load_alg('SVM-original')
    data = util.load_pkl(feature_path)
    bit_twiddle_params(a, data, util.features)
    
    # param_dist = {'penalty':['l1', 'l2'], 'C':[10**i for i in range(-5, 5)]}
    # a.search(data, param_dist, ['graph_features'])
