# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : recall_sample_maker.py.py
# Time       ：2023/8/30 13:44
# Author     ：aliang
"""

from rec.utils.common import read_config, read_data, sink
import nacos
import pandas as pd
from rec.utils.connection import CephClient
from rec.utils.connection import Connection as Con
from collections import defaultdict
from rec.utils.common import gen_cfg_name, gen_global_cfg_name


class RecallSampleMaker(object):
    def __init__(self, config=None, customer_id=None, project_id=None, scene_id=None):
        """
        config：1、指定路径加载配置
                2、传入配置
                3、nacos自动加载配置
        mode：1、本地磁盘运行
              2、远程ceph下载
        """
        cfg_info = [customer_id, project_id, scene_id]
        if isinstance(config, str):
            self.project_cfg = read_config(config)
            self.recall_cfg = read_config(self.project_cfg[gen_cfg_name('recall', cfg_info)])
            self.con_cfg = read_config(self.project_cfg[gen_global_cfg_name('connection', customer_id)])
        elif isinstance(config, dict):
            self.recall_cfg = config[gen_cfg_name('recall', cfg_info)]
            self.con_cfg = config[gen_global_cfg_name('connection', customer_id)]
        else:
            self.autoNacos = nacos.AutoNacos()
            self.recall_cfg = self.autoNacos.get_config(gen_cfg_name('recall', cfg_info))
            self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))
        self.con = Con(self.con_cfg)
        self.CephClient = CephClient(self.con_cfg)

    def transform_node(self, df, data_info):
        data = defaultdict(list)
        for index, row in df.groupby(by=[data_info['user_id']]):
            item_list = row[data_info['item_id']].tolist()
            if len(item_list) > 1:
                for index in range(len(item_list) - 1):
                    data['head'].append(item_list[index])
                    data['tail'].append(item_list[index+1])
        df = pd.DataFrame(data, columns=['head', 'tail'])
        return df

    def transform(self):
        data_info = self.recall_cfg['data_info']
        df = read_data(self.recall_cfg['source_db_info'], ceph=self.CephClient)
        df = df[df['label'] == 1]
        df = df.sort_values(by=[data_info['user_id']], ascending=[True])
        df = df[[data_info['user_id'], data_info['item_id']]]
        df = self.transform_node(df, data_info)
        sink(df, self.recall_cfg['sample_db_info'], ceph=self.CephClient)


if __name__ == '__main__':
    config = '../config/project.yaml'
    rsm = RecallSampleMaker(config)
    rsm.transform()