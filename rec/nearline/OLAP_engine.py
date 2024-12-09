# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : statistics_engine.py
# Time       ：2023/8/10 21:24
# Author     ：aliang
"""
import os
import nacos
import pandas as pd
from realtime_rec.utils.common import read_config
from realtime_rec.utils.connection import Connection as Con
from realtime_rec.op.olap_op import OLAPOp
from realtime_rec.utils.connection import CephClient
from realtime_rec.utils.common import read_config, gen_cfg_name, gen_global_cfg_name


class OLAPEngine(object):
    def __init__(self, nacos_file=None, customer_id=None):
        self.autoNacos = nacos.AutoNacos(nacos_file=nacos_file)
        self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))
        self.OLAP_cfg = self.autoNacos.get_config(gen_global_cfg_name('OLAP', customer_id))

        self.CephClient = CephClient(self.con_cfg)
        self.con = Con(self.con_cfg)
        self.OLAP = OLAPOp

    def read_table(self, db_info):
        """
        读取数据
        """
        if db_info['sink_mode'] == 'local':
            df = pd.read_csv(db_info['source_path'])
        elif db_info['sink_mode'] == 'mysql':
            con = self.con.mysql_con()
            df = pd.read_sql(db_info['source_path'], con)
            con.close()
        elif db_info['sink_mode'] == 'ceph':
            save_file_dir = '../../cache'
            bucket_name = db_info['bucket_name']
            save_file_name = os.path.join(save_file_dir, os.path.basename(db_info['source_path']))
            key_name = db_info['source_path']
            ret = self.CephClient.download_file(save_file_name=save_file_name,
                                                bucket_name=bucket_name,
                                                key_name=key_name,
                                                always_overwrite=True)
            df = pd.read_csv(save_file_name)
        else:
            raise Exception('err sink_mode')
        return df

    def sink(self, result_dict):
        sql = "select goods_sn from online_goods where is_recommend='1' and (is_on_sale='1' or whole_is_on_sale='1');"
        data = pd.read_sql(sql, self.con.mysql_con(database='k11'))
        rec_items = data['goods_sn'].tolist()
        self.redis_con = self.con.redis_con()
        for k, v in result_dict.items():
            v = [i for i in v if i in rec_items]
            self.redis_con.delete(k)
            self.redis_con.lpush(k, *v)
            print(self.redis_con.lrange(k, 0, -1))

    def run(self):
        df = self.read_table(self.OLAP_cfg['behavior_db_info'])
        operators = self.OLAP_cfg['OLAP_operators']
        for operator in operators:
            op = operator['op']
            params = operator['params']
            func = getattr(self.OLAP, op)
            result_dict = func(df, params)
            self.sink(result_dict)