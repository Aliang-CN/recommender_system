# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : rank_sample_maker.py
# Time       ：2023/8/26 19:30
# Author     ：aliang
"""
import pickle
from rec.utils.connection import Connection as Con
from rec.utils.common import read_data, sink
from rec.utils.common import read_config, deepctr_feature_encode,\
    deepctr_gen_feature_encode_dict, deepctr_get_cols_order, deepctr_get_cols_type
import nacos
import pandas as pd
from rec.utils.common import gen_cfg_name, gen_global_cfg_name
from rec.utils.connection import CephClient


class RankSampleMaker(object):
    def __init__(self, customer_id=None, project_id=None, scene_id=None):
        """
        config：1、指定路径加载配置
                2、传入配置
                3、nacos自动加载配置
        mode：1、本地磁盘运行
              2、远程ceph下载
        """
        cfg_info = [customer_id, project_id, scene_id]
        self.autoNacos = nacos.AutoNacos()
        self.rank_cfg = self.autoNacos.get_config(gen_cfg_name('rank', cfg_info))
        self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))
        self.con = Con(self.con_cfg)
        self.CephClient = CephClient(self.con_cfg)

    def transform(self):
        self.data = read_data(self.rank_cfg['widetable_db_info'], self.con.mysql_con(), self.CephClient)
        self.cols_order = deepctr_get_cols_order(self.rank_cfg)
        self.cols_type = deepctr_get_cols_type(self.rank_cfg)
        self.data = self.data[self.cols_order]                           # 按照指定列排序
        self.enc_dict = deepctr_gen_feature_encode_dict(self.data, self.rank_cfg)
        self.result_data = deepctr_feature_encode(self.data, self.cols_type, self.enc_dict)
        sink(self.enc_dict, self.rank_cfg['enc_db_info'], self.CephClient)
        sink(self.result_data, self.rank_cfg['sample_db_info'], self.CephClient)


if __name__ == '__main__':
    rsm = RankSampleMaker()
    rsm.transform()