# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : etl_engine.py
# Time       ：2021/8/30 13:55
# Author     ：aliang
"""

import sys
sys.path.append('../../')
import nacos
from rec.utils.common import read_data, sink
from rec.op.etl_op import ETLOp
from rec.utils.connection import Connection as Con
from rec.utils.connection import CephClient
from rec.utils.common import read_config, gen_cfg_name, gen_global_cfg_name


class ETLEngine(object):
    def __init__(self, config=None, customer_id=None, project_id=None, scene_id=None):
        info = [customer_id, project_id, scene_id]
        if isinstance(config, str):
            self.project_cfg = read_config(config)
            self.etl_cfg = read_config(self.project_cfg[gen_cfg_name('etl', info)])
            self.con_cfg = read_config(self.project_cfg[gen_global_cfg_name('connection', customer_id)])
        elif isinstance(config, dict):
            self.recall_cfg = config[gen_cfg_name('etl', info)]
            self.con_cfg = config[gen_global_cfg_name('connection', customer_id)]
        else:
            self.autoNacos = nacos.AutoNacos()
            self.etl_cfg = self.autoNacos.get_config(gen_cfg_name('etl', info))
            self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))
        print(self.etl_cfg)
        print(self.con_cfg)
        self.CephClient = CephClient(self.con_cfg)
        self.con = Con(self.con_cfg)
        self.etl = ETLOp

    def transform(self, db_info, operators):
        df = read_data(db_info['source_db_info'], self.con.mysql_con())
        for operator in operators:
            op = operator['op']
            params = operator['params']
            func = getattr(self.etl, op)
            df = func(df, params)
        sink(df, db_info['etled_db_info'], ceph=self.CephClient)

    def deal_with_user_data(self):
        db_info = self.etl_cfg['user_db_info']
        user_operators = self.etl_cfg['user_operators']
        self.transform(db_info, user_operators)

    def deal_with_item_data(self):
        db_info = self.etl_cfg['item_db_info']
        item_operators = self.etl_cfg['item_operators']
        self.transform(db_info, item_operators)

    def deal_with_behavior_data(self):
        db_info = self.etl_cfg['behavior_db_info']
        behavior_operators = self.etl_cfg['behavior_operators']
        self.transform(db_info, behavior_operators)

    def join_data(self):
        db_info = self.etl_cfg['join_db_info']
        join_operators = self.etl_cfg['join_operators']
        item_df = read_data(self.etl_cfg['item_db_info']['etled_db_info'], ceph=self.CephClient)
        user_df = read_data(self.etl_cfg['user_db_info']['etled_db_info'], ceph=self.CephClient)
        behavior_df = read_data(self.etl_cfg['behavior_db_info']['etled_db_info'], ceph=self.CephClient)
        user_df_cols = user_df.columns.tolist()
        item_df_cols = item_df.columns.tolist()
        for operator in join_operators:
            op = operator['op']
            params = operator['params']
            func = getattr(self.etl, op)
            behavior_df = func(behavior_df, user_df, item_df, params)
        cols = user_df_cols + item_df_cols + ['label']
        behavior_df = behavior_df[cols]
        sink(behavior_df, db_info, ceph=self.CephClient)
