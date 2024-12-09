#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/18 上午10:45
# @Author  : Aiang
# @File    : recall_sample_maker_itemcf.py


from rec.utils.common import read_config, read_data, sink
import nacos
from rec.utils.connection import CephClient
from rec.utils.connection import Connection as Con
from collections import defaultdict
from rec.utils.common import gen_cfg_name, gen_global_cfg_name


class ItemCFRecallSampleMaker(object):
    def __init__(self, customer_id=None, project_id=None, scene_id=None, data_id=None):
        """
        config：1、指定路径加载配置
                2、传入配置
                3、nacos自动加载配置
        mode：1、本地磁盘运行
              2、远程ceph下载
        """
        info = [customer_id, project_id, scene_id, data_id]
        self.autoNacos = nacos.AutoNacos()
        self.recall_cfg = self.autoNacos.get_config(gen_cfg_name('itemcf_recall_sample_maker', info))['spec']
        self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))
        self.con = Con(self.con_cfg)
        self.CephClient = CephClient(self.con_cfg)

    def transform(self):
        data_info = self.recall_cfg['params']['data_info']
        df = read_data(self.recall_cfg['inputs']['main'], con=self.con.mysql_con(), ceph=self.CephClient)
        columns = {data_info['user_id']: 'user_id', data_info['item_id']: 'item_id', data_info['timestamp']: 'timestamp'}
        df.rename(columns=columns, inplace=True)
        sink(df, self.recall_cfg['outputs']['main'], ceph=self.CephClient)


if __name__ == '__main__':
    print('start itemcf_recall_sample_maker')
    customer_id = 'k11'
    project_id = 'online'
    scene_id = '001'
    data_id = '01'
    mt = ItemCFRecallSampleMaker(customer_id=customer_id, project_id=project_id,
                                 scene_id=scene_id, data_id=data_id)
    mt.transform()
    print('done')
