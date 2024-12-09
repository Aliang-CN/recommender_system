# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : cluster_trainer.py
# Time       ：2023/10/8 15:05
# Author     ：aliang
"""

import nacos
import pandas as pd
from rec.utils.common import gen_cfg_name, gen_global_cfg_name
from rec.utils.common import read_data
from rec.utils.connection import CephClient


class ClusterTrainer(object):
    def __init__(self, customer_id=None, scene_id=None, experiment_id=None):
        cfg_info = [customer_id, scene_id, experiment_id]
        self.autoNacos = nacos.AutoNacos()
        self.cluster_cfg = self.autoNacos.get_config(gen_cfg_name('cluster', cfg_info))
        self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))
        self.model_cfg = self.autoNacos.get_config(self.cluster_cfg['model'])
        self.CephClient = CephClient(self.con_cfg)
        self.data = read_data(self.cluster_cfg['sample_db_info'], ceph=self.CephClient)
        self._init_model()

    def _init_model(self):
        cluster_module = __import__('sklearn.cluster')
        self.cluster_class = getattr(cluster_module.cluster, 'MiniBatchKMeans')
        self.cluster_class = self.cluster_class(**self.model_cfg['params'])

    def execute(self):
        cluster_scale = self.cluster_class.fit(self.data[1:])
        self.result = cluster_scale.predict(self.data[1:])

    def transfomer(self):
        self.data['cluster_tag'] = self.result

    def get_result(self):
        user_to_cluster_dict = self.data[['user_id', 'cluster_tag']].to_dict('records')
        cluster_to_user_dict = {}
        for cluser_tag, row in self.data.groupby('cluser_tag'):
            user_list = row['user_id'].tolist()
            cluster_to_user_dict[cluser_tag] = user_list
        return user_to_cluster_dict, cluster_to_user_dict