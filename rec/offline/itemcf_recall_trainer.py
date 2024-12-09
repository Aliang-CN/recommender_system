#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/25 下午5:44
# @Author  : Aiang
# @File    : itemcf_recall_trainer.py
# desc     :

import os
import nacos
import time
import hashlib
import pandas as pd
from collections import defaultdict
from rec.utils.connection import Connection as Con
from rec.utils.connection import CephClient
from rec.models.recall_models.item_cf import ItemCF
from rec.utils.common import gen_cfg_name, gen_global_cfg_name
from rec.utils.common import read_data


class ItemCFRecallTrainer(object):
    def __init__(self, customer_id=None, project_id=None, scene_id=None, data_id=None):
        info = [customer_id, project_id, scene_id, data_id]
        self.customer_id = customer_id
        self.project_id = project_id
        self.scene_id = scene_id
        self.data_id = data_id
        self.autoNacos = nacos.AutoNacos()
        self.recall_cfg = self.autoNacos.get_config(gen_cfg_name('itemcf_recall_trainer', info))['spec']
        self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))
        self.model_name = self.recall_cfg['params']['model']
        self.model_cfg = self.autoNacos.get_config(gen_cfg_name(self.model_name, info))
        self.con = Con(self.con_cfg)
        self.CephClient = CephClient(self.con_cfg)
        self.load()
        self._init_model()

    def _init_model(self):
        self.model = ItemCF(self.model_cfg)

    def prepare_data(self, src, target):
        nick_id, item_id = src
        hist_item, hist_mask = target
        return nick_id, item_id, hist_item, hist_mask

    def load(self):
        self.train_data = read_data(self.recall_cfg['inputs']['main'], ceph=self.CephClient)

    def sink(self, df: pd.DataFrame, db_info: dict):
        """
        保存embedding
        """
        if db_info['mode'] == 'local':
            df.to_csv(db_info['sink_path'], encoding='utf_8_sig', index=False)
        elif db_info['mode'] == 'ceph':
            save_file_dir = '../../cache'
            bucket_name = self.customer_id
            datatime = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
            model_name = f'itemcf_{self.customer_id}_{self.project_id}_{self.scene_id}_{self.data_id}.csv.{datatime}'

            model_md5_name = f'itemcf_{self.customer_id}_{self.project_id}_{self.scene_id}_{self.data_id}.csv-tag'

            # 保存本地缓存
            model_save_cache_file_path = save_file_dir + '/' + model_name
            model_md5_save_cache_file_path = save_file_dir + '/' + model_md5_name

            df.to_csv(model_save_cache_file_path, encoding='utf_8_sig', index=False)
            md5val = hashlib.md5(open(model_save_cache_file_path, 'rb').read()).hexdigest()
            with open(model_md5_save_cache_file_path, 'w') as f:
                data = md5val + " " + model_name
                f.write(data)

            # 上传ceph
            model_key_name = db_info['sink_dir_path'] + '/' + model_name
            model_md5_key_name = db_info['sink_dir_path'] + '/' + model_md5_name
            ret = self.CephClient.upload_file(upload_file_name=model_save_cache_file_path,
                                              bucket_name=bucket_name,
                                              key_name=model_key_name)
            ret = self.CephClient.upload_file(upload_file_name=model_md5_save_cache_file_path,
                                              bucket_name=bucket_name,
                                              key_name=model_md5_key_name)
            os.remove(model_save_cache_file_path)
            os.remove(model_md5_save_cache_file_path)

    def fit(self):
        print('[INFO] Model: {} Start Training'.format(self.model_cfg['model_name']))
        self.model.fit(self.train_data)

    def save(self):
        db_info = self.recall_cfg['outputs']['main']
        model = self.model.get_result()
        data = defaultdict(list)
        for item, corr_item_list in model.items():
            data['item_id'].append(item)
            field_list = []
            for corr_item, score in corr_item_list.items():
                field = str(corr_item) + ':' + str(score)
                field_list.append(field)
            data['field_list'].append("|".join(field_list))
        df = pd.DataFrame(data, columns=['item_id', 'field_list'])
        self.sink(df, db_info)


if __name__ == '__main__':
    customer_id = 'k11'
    project_id = 'online'
    scene_id = '001'
    data_id = '01'
    RT = ItemCFRecallTrainer(customer_id=customer_id, project_id=project_id, scene_id=scene_id, data_id=data_id)
    RT.fit()
    RT.save()

