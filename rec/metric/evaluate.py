# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : evluate.py
# Time       ：2023/9/10 11:07
# Author     ：aliang
"""

import numpy as np
import pandas as pd
from rec.metric.custom_metric import precision_at_k, recall_at_k, map_at_k, hr_at_k, ndcg_at_k, mrr_at_k
from sklearn.metrics import log_loss, roc_auc_score
import tensorflow as tf


def evaluate_rank(preds, test_gd, k=10):
    metric_dict = dict()
    tmp_preds = preds.copy()
    tmp_preds = {key: rank_list[:k] for key, rank_list in tmp_preds.items()}

    pre_k = np.mean([precision_at_k(r, k) for r in tmp_preds.values()])
    rec_k = recall_at_k(tmp_preds, test_gd, k)
    hr_k = hr_at_k(tmp_preds, test_gd)
    map_k = map_at_k(tmp_preds.values())
    mrr_k = mrr_at_k(tmp_preds, k)
    ndcg_k = np.mean([ndcg_at_k(r, k) for r in tmp_preds.values()])

    metric_dict['pre@{}'.format(k)] = pre_k
    metric_dict['rec@{}'.format(k)] = rec_k
    metric_dict['hr@{}'.format(k)] = hr_k
    metric_dict['map@{}'.format(k)] = map_k
    metric_dict['mrr@{}'.format(k)] = mrr_k
    metric_dict['ndcg@{}'.format(k)] = ndcg_k

    return metric_dict


def evaluate_recall(preds, test_gd, k=10):
    metric_dict = dict()
    tmp_preds = preds.copy()
    tmp_preds = {key: rank_list[:k] for key, rank_list in tmp_preds.items()}
    pre_k = np.mean([precision_at_k(r, k) for r in tmp_preds.values()])
    rec_k = recall_at_k(tmp_preds, test_gd, k)
    hr_k = hr_at_k(tmp_preds, test_gd)
    map_k = map_at_k(tmp_preds.values())
    mrr_k = mrr_at_k(tmp_preds, k)
    ndcg_k = np.mean([ndcg_at_k(r, k) for r in tmp_preds.values()])
    metric_dict['pre@{}'.format(k)] = pre_k
    metric_dict['rec@{}'.format(k)] = rec_k
    metric_dict['hr@{}'.format(k)] = hr_k
    metric_dict['map@{}'.format(k)] = map_k
    metric_dict['mrr@{}'.format(k)] = mrr_k
    metric_dict['ndcg@{}'.format(k)] = ndcg_k
    return metric_dict


def evaluate_ctr(y_true, y_pre):
    metric_dict = dict()
    auc_score = roc_auc_score(y_true, y_pre)
    metric_dict['auc'] = auc_score
    return metric_dict


def auroc(y_true, y_pred):
    return tf.compat.v1.py_func(roc_auc_score, (y_true, y_pred), tf.double)
