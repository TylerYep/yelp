import pandas as pd
import numpy as np
import sklearn
import pickle
from sklearn.metrics import precision_recall_fscore_support, r2_score, mean_squared_error
from sklearn.model_selection import RandomizedSearchCV

import os, sys
sys.path.append('ml')
import util

def load_alg(name):
    path = 'data/ml/results/' + name +'.pkl'
    if os.path.isfile(path):
        return util.load_pkl(path)
    model_name = name.split('-')[0]
    return Algorithm(name, util.model_dict[model_name])

class Algorithm:
    def __init__(self, name, model):
        """
        Args:
            name: name of model
            model: uninstantiated sklearn model
        """
        self.name = name
        self.model = model
        self.results = pd.DataFrame(columns=util.results_headers)

    def get_fname(self):
        # Returns the file path to save
        fname = self.name
        fname += '.pkl'
        return os.path.join('data/ml/results', fname)

    def save(self):
        util.save_pkl(self.get_fname(), self)

    def predict(self, x):
        return self.clf.predict(x)

    def train(self, x, y):
        self.clf.fit(x, y)
        preds = self.predict(x)
        return mean_squared_error(y, preds)
        # return util.get_acc(y, preds)

    def eval(self, x, y):
        predictions = self.predict(x)
        # test_error = util.get_acc(y, predictions)
        test_error = mean_squared_error(y, predictions)
        return test_error


    def run(self, data, features, clf_options={}):
        """
        Arguments
            data: DataFeatures object
            features: list of features
            clf_options: dictionary of sklearn classifier options
        """
        self.clf = self.model(**clf_options)
        X = data.get_joint_matrix(util.features)
        train_x = X[data.train_indices]
        train_y = data.labels[data.train_indices]
        val_x = X[data.val_indices]
        val_y = data.labels[data.val_indices]
        test_x = X[data.test_indices]
        test_y = data.labels[data.test_indices]

        train_acc = self.train(train_x, train_y)
        dev_acc = self.eval(val_x, val_y)
        test_acc = self.eval(test_x, test_y)
        
        # Add a row to results
        row = (self.name, str(clf_options), train_acc, dev_acc, test_acc)
        self.results.loc[len(self.results)] = row
        self.save()

    def search(self, data, param_dist, features):
        X = data.get_joint_matrix(features)
        y = data.labels
        r_search = RandomizedSearchCV(self.model(), param_dist, n_iter=20)
        r_search.fit(X, y)
        self.r = r_search

    def to_csv(self):
        self.results.to_csv(os.path.join('data/ml/results', self.name + '.csv'), index=False)
