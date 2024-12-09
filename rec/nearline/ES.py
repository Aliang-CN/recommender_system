# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : ES.py
# Time       ：2023/8/27 20:40
# Author     ：aliang
"""

import pandas as pd
from rec.utils.connection import Connection as Con
from elasticsearch import helpers
from tqdm import tqdm
import nacos
from rec.op.es_op import ESOp
from rec.utils.common import read_config
from rec.utils.connection import CephClient


class ESEngine(object):
    def __init__(self, config=None):
        if isinstance(config, str):
            self.project_cfg = read_config(config)
            self.con_cfg = read_config(self.project_cfg['connection'])
            self.es_cfg = read_config(self.project_cfg['es'])
        elif isinstance(config, dict):
            self.es_cfg = config['es']
            self.con_cfg = config['connection']
        else:
            self.autoNacos = nacos.AutoNacos()
            self.con_cfg = self.autoNacos.get_config('connection')
            self.es_cfg = self.autoNacos.get_config('es')
        self.con = Con(self.con_cfg)
        self.CephClient = CephClient(self.con_cfg)
        self.es_con = Con().es_con()
        self.es = ESOp

    def read_table(self, db_info):
        """
        读取数据
        """
        # read data
        if db_info['sink_mode'] == 'local':
            df = pd.read_csv(db_info['source_path'])
        elif db_info['sink_mode'] == 'mysql':
            con = self.con.mysql_con()
            df = pd.read_sql(con, db_info['source_path'])
            con.close()
        else:
            raise Exception('err sink_mode')
        return df

    def sink(self, data_list: list, db_info: dict):
        action = [{"_index": db_info['sink_index'],
                   "_type": db_info['sink_type'],
                   '_id': d[db_info['sink_id']],
                   "_source": d} for d in data_list]
        helpers.bulk(self.es_con, action)

    def transform(self, db_info, operators):
        df = self.read_table(db_info)
        data_list = df.to_dict('record')
        for operator in operators:
            op = operator['op']
            params = operator['params']
            func = getattr(self.es, op)
            data_list = func(data_list, params)
        self.sink(data_list, db_info)

    def sync_online_goods_to_es(self, config):
        db_info = config['user_db_info']
        operators = config['user_operators']
        self.transform(db_info, operators)

    def sync_offline_goods_to_es(self, config):
        db_info = config['user_db_info']
        operators = config['user_operators']
        self.transform(db_info, operators)


if __name__ == '__main__':
    es = ESEngine(config='../config/project.yaml')
    # es.write()