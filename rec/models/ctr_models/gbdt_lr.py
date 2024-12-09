# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : gdbt_lr.py
# Time       ：2021/10/8 15:29
# Author     ：linxingliang
"""

import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import joblib


class GDBT_LR(object):
    def __init__(self, params):
        self.params = params
        self._init_model()

    def _init_model(self):
        self.lgb_model = lgb.LGBMClassifier(**self.params['lgb_params'])
        self.lr_model = LogisticRegression(**self.params['lr_params'])

    def fit(self, data):
        train = data[:-1]
        target = data[-1]
        X, val_X, y, val_y = train_test_split(train, target, test_size=0.2, random_state=2021)
        self.lgb_model.fit(X, y, eval_set=[(X, y), (val_X, val_y)], eval_names=['train', 'val'],
                           eval_metric=['auc', 'binary_logloss'], verbose=200)
        gbdt_feats = self.lgb_model.predict(train, pred_leaf=True)
        gbdt_feats_name = ['gbdt_leaf_' + str(i) for i in range(self.params['lgb_params']['n_estimators'])]
        lr_input_data = pd.DataFrame(gbdt_feats, columns=gbdt_feats_name)
        for col in gbdt_feats_name:
            encoder = LabelEncoder().fit(lr_input_data[col])
            lr_input_data[col] = encoder.transform(lr_input_data[col])
        x_train, x_val, y_train, y_val = train_test_split(lr_input_data, target, test_size=0.2, random_state=2018)
        self.lr_model.fit(x_train, y_train)

    def save_model(self, lgb_path, lr_path):
        joblib.dump(self.lgb_model, lgb_path)
        joblib.dump(self.lr_model, lr_path)
