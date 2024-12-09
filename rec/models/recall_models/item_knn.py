# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : itemknn.py
# Time       ：2023/10/11 11:24
# Author     ：aliang
"""


import numpy as np
import pandas as pd
from scipy.sparse import csc_matrix
import argparse
from datetime import datetime
from tqdm import tqdm
from collections import defaultdict
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity


class ItemKNN:
    def __init__(self, params):
        print("%s Params: %s" % (datetime.now(), params))
        self._read_dataset(params.get("train_data"), params.get("test_data"))
        self.similarity_measure = params.get("similarity_measure")
        self.num_neighbors = params.get("num_neighbors")
        self.renormalize_similarity = params.get("renormalize_similarity")
        self.enable_average_bias = params.get("enable_average_bias")
        self.metrics = params.get("metrics")
        self.min_similarity_threshold = params.get("min_similarity_threshold")

    def _read_dataset(self, train_data, test_data):
        print("%s Reading dataset..." % datetime.now())
        train = pd.read_csv(train_data, sep="\t").values.astype(int)
        test = pd.read_csv(test_data, sep="\t").values.astype(int)
        total = np.vstack([train, test])
        self.nUsers = len(np.unique(total[:, 0]))
        self.nItems = len(np.unique(total[:, 1]))
        print("%s Number of users: %d, number of items: %d" % (datetime.now(),  self.nUsers, self.nItems))
        self.trainIUMatrix = csc_matrix((np.ones(len(train)), train.T),
                                        shape=(self.nUsers, self.nItems)).T # row:item, col:user
        self.test_items = defaultdict(list)
        for row in test:
            self.test_items[row[0]].append(row[1])

    def fit(self):
        self.sim_matrix = self.get_pairwise_similarity()
        self.sim_matrix[np.isnan(self.sim_matrix)] = -1
        if self.renormalize_similarity:
            self.sim_matrix = (self.sim_matrix + 1) / 2             # map to 0 ~ 1
        self.sim_matrix[self.sim_matrix < self.min_similarity_threshold] = 0 # remove similar values less than threshold
        item_indexes = np.argpartition(-self.sim_matrix, self.num_neighbors)[:, self.num_neighbors:] # pick the smallest
        self.sim_matrix[np.arange(item_indexes.shape[0])[:, np.newaxis], item_indexes] = 0
        self.sim_matrix = normalize(self.sim_matrix, norm='l1', axis=1)
        print('%s Finished similarity matrix computation.' % datetime.now())

    def predict(self):
        print('%s Start predicting preference...' % datetime.now())
        trainIUMatrix = self.trainIUMatrix.toarray()
        if self.enable_average_bias:
            item_mean = np.mean(trainIUMatrix, axis=1, keepdims=True)
            pred_matrix = np.dot(self.sim_matrix, trainIUMatrix - item_mean) + item_mean
        else:
            pred_matrix = np.dot(self.sim_matrix, trainIUMatrix)
        pred_matrix[trainIUMatrix > 0] = -np.inf # remove clicked items in train data
        return pred_matrix.T

    def evaluate(self):
        '''compute hitrate, recall, NDCG @ topK'''
        self.evaluate_metrics(self.predict(), self.test_items, self.metrics)

    def get_pairwise_similarity(self):
        print('%s Start computing similarity matrix...' % datetime.now())
        if self.similarity_measure == 'pearson':
            return np.corrcoef(self.trainIUMatrix.toarray()) - 2 * np.eye(self.nItems)              # set diagnal to -1
        elif self.similarity_measure == 'cosine':
            return cosine_similarity(self.trainIUMatrix.toarray()) - 2 * np.eye(self.nItems)        # set diagnal to -1
        else:
            raise NotImplementedError("similarity_measure=%s is not supported." % self.similarity_measure)

    def evaluate_metrics(self, pred_matrix, test_user2items, metrics):
        num_users = len(pred_matrix)
        print("{} Evaluating metrics for {:d} users...".format(datetime.now(), num_users))
        metric_callers = []
        max_topk = 0
        for metric in metrics:
            try:
                metric_callers.append(eval(metric))
                max_topk = max(max_topk, int(metric.split("k=")[-1].strip(")")))
            except:
                raise NotImplementedError('metrics={} not implemented.'.format(metric))

        topk_items_chunk = np.argpartition(-pred_matrix, range(max_topk))[:, 0:max_topk]
        true_items_chunk = [test_user2items[user_index] for user_index in range(num_users)]
        results = [[fn(topk_items, true_items) for fn in metric_callers] \
                   for topk_items, true_items in zip(topk_items_chunk, true_items_chunk)]
        average_result = np.average(np.array(results), axis=0).tolist()
        return_dict = dict(zip(metrics, average_result))
        print('%s [Metrics] ' % datetime.now() + ' - '.join(
            '{}: {:.6f}'.format(k, v) for k, v in zip(metrics, average_result)))
        return return_dict