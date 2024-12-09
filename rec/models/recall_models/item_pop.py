# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : itempop.py
# Time       ：2023/10/11 12:00
# Author     ：aliang
"""


class ItemPop(object):
    def __init__(self, n=400):
        self.rank_list = None
        self.N = n

    def fit(self, train_set):
        res = train_set['item_id'].value_counts()
        self.rank_list = res.index.tolist()[:self.N]

    def predict(self, test_ur, train_ur, topk=10):
        res = {}
        for user in test_ur.keys():
            candidates = self.rank_list
            candidates = [item for item in candidates if item not in train_ur[user]]
            if len(candidates) < topk:
                raise Exception(f'parameter N is too small to get {topk} recommend items')
            res[user] = candidates[:topk]
        return res
