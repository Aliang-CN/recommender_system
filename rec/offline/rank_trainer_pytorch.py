# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : rank_trainer_pytorch.py
# Time       ：2023/9/14 17:36
# Author     ：aliang
"""
import pickle
import torch
from rec.utils.common import read_config, get_feature_columns, get_feature_columns_torch
import os
import numpy as np
from deepctr_torch.models import *
from rec.utils.connection import CephClient
from rec.metric.evaluate import evaluate_ctr
from rec.utils.common import read_data, deepctr_get_cols_type, deepctr_get_model_cols_order
import nacos


class RankTrainer(object):
    def __init__(self, config=None, mode='local'):
        if isinstance(config, str):
            self.project_cfg = read_config(config)
            self.data_cfg = read_config(self.project_cfg['data'])
            self.rank_cfg = read_config(self.project_cfg['online_rank'])
            self.con_cfg = read_config(self.project_cfg['connection'])
            self.model_cfg = read_config(os.path.join('../config/ctr', self.rank_cfg['model'] + '.yaml'))
        elif isinstance(config, dict):
            self.data_cfg = config['data']
            self.rank_cfg = config['online_rank']
            self.con_cfg = config['connection']
            self.model_cfg = config[self.rank_cfg['model']]
        else:
            self.autoNacos = nacos.AutoNacos()
            self.data_cfg = self.autoNacos.get_config("data")
            self.rank_cfg = self.autoNacos.get_config('online_rank')
            self.con_cfg = self.autoNacos.get_config('connection')
            self.model_cfg = self.autoNacos.get_config(self.rank_cfg['model'])
        self.CephClient = CephClient(self.con_cfg)
        self.mode = mode

        self.result_data = self.read_data()
        self.enc_dict = self.read_enc_dict()
        self._init_model()

    def read_data(self):
        # TODO 后面由deep runtime传训练数据进来
        if self.mode == 'local':
            rank_train_path = '../../data/' + self.data_cfg['rank_train_path'] + '/train.pkl'
            with open(rank_train_path, 'rb') as f:
                data = pickle.load(f)
        elif self.mode == 'ceph':
            pass
        return data

    def read_enc_dict(self):
        if self.mode == 'local':
            enc_dict_path = '../../' + self.data_cfg['encode_dict_path'] + '/enc_data.pkl'
            with open(enc_dict_path, 'rb') as f:
                enc_dict = pickle.load(f)
        elif self.mode == 'ceph':
            pass
        return enc_dict

    def _init_model(self):
        """
        初始化模型
        """
        self.params = self.model_cfg['params']
        self.cols_type = deepctr_get_cols_type(self.rank_cfg)
        self.cols_order = deepctr_get_model_cols_order(self.rank_cfg)
        self.linear_feature_columns = get_feature_columns_torch(self.cols_type, self.enc_dict)
        self.dnn_feature_columns = get_feature_columns_torch(self.cols_type, self.enc_dict)
        self.params['linear_feature_columns'] = self.linear_feature_columns
        self.params['dnn_feature_columns'] = self.dnn_feature_columns
        self.params['task'] = 'binary'
        self.model = eval('{}(**self.params)'.format(self.model_cfg['model_name']))
        self.model.compile("adagrad", "binary_crossentropy", metrics=["binary_crossentropy", "auc"], )

    def execute(self):
        train_data = {name: self.result_data[name] for name in self.cols_order}
        label = np.array(self.result_data['label'])
        if len(label.shape) == 1:
            label = label.T
        self.model.fit(train_data, label,
                       batch_size=self.model_cfg['batch_size'],
                       epochs=self.model_cfg['n_epoch'],
                       verbose=2,
                       validation_split=0.2)

    def save_model(self):
        if self.mode == 'local':
            model_path = '../../' + '{}/{}'.format(self.data_cfg['rank_model_path'], self.rank_cfg['model']) + \
                         '/model.pkl'
            torch.save(self.model, model_path)
        elif self.mode == 'ceph':
            pass

    def evaluate(self, test_data):
        pred_ans = self.model.predict(test_data, batch_size=2560).reshape(-1)
        result = evaluate_ctr(test_data, pred_ans)
        return result


if __name__ == '__main__':
    config = '../config/project.yaml'
    rt = RankTrainer(config)
    rt.execute()
    rt.save_model()