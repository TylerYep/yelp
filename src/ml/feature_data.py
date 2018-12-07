import pickle
import numpy as np
import sklearn
import pandas as pd
from sklearn.model_selection import train_test_split
from collections import Counter, defaultdict
from restaurant_analysis import load_graph

import os, sys
sys.path.append('algorithms')
import util

class DataFeatures:
    def __init__(self):
        self.raw = load_graph()
        self.feature_matrix = self.raw
        self.fname = 'data/ml/graph_features.pkl'

        self.train_indices = self.raw.index #[self.raw.split == 0]
        self.val_indices = self.raw.index #[self.raw.split == 1]
        self.test_indices = self.raw.index #[self.raw.split == 2]

        self.labels = self.raw.review_count.values
        self.save()

    def get_f_dict(self):
        return dict(zip(util.features, [self.feature_matrix]))

    def get_joint_matrix(self, features):
        f_dict = self.get_f_dict()
        X = [f_dict[f] for f in features]
        X = np.concatenate(tuple(X), axis=1)
        return X

    def save(self):
        util.save_pkl(self.fname, self)


if __name__ == "__main__":
    x = DataFeatures()
