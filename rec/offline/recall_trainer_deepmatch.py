# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : recall_trainer_deepmatch.py
# Time       ：2023/10/21 16:41
# Author     ：aliang
"""
import os
import nacos
from deepmatch.models import *
from realtime_rec.utils.common import load_recall_model, read_config
from realtime_rec.utils.connection import Connection as Con
from realtime_rec.utils.connection import CephClient
import pandas as pd
import networkx as nx
import grpc
import hashlib
import time
import uuid
from realtime_rec.utils.common import gen_cfg_name, gen_global_cfg_name


class RecallTrainer(object):
    def __init__(self, config=None, customer_id=None, scene_id=None, experiment_id=None):
        """
        config：1、指定路径加载配置
                2、传入配置
                3、nacos自动加载配置
        mode：1、本地磁盘运行
              2、远程ceph下载
        """
        cfg_info = [customer_id, scene_id, experiment_id]
        if isinstance(config, str):
            self.project_cfg = read_config(config)
            self.recall_cfg = read_config(self.project_cfg[gen_cfg_name('recall', cfg_info)])
            self.con_cfg = read_config(self.project_cfg[gen_global_cfg_name('connection', customer_id)])
            self.model_cfg = read_config(os.path.join('../config/recall', self.recall_cfg['model'] + '.yaml'))
        elif isinstance(config, dict):
            self.recall_cfg = config[gen_cfg_name('recall', cfg_info)]
            self.con_cfg = config[gen_global_cfg_name('connection', customer_id)]
            self.model_cfg = config[self.recall_cfg['model']]
        else:
            self.autoNacos = nacos.AutoNacos()
            self.recall_cfg = self.autoNacos.get_config(gen_cfg_name('recall', cfg_info))
            self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))
            self.model_cfg = self.autoNacos.get_config(self.recall_cfg['model'])
        self.con = Con(self.con_cfg)
        self.CephClient = CephClient(self.con_cfg)
        self.graph = self.read_graph(self.recall_cfg['sample_db_info'])
        self._init_model()

    def read_graph(self, db_info):
        if db_info['mode'] == 'local':
            G = nx.read_edgelist(db_info['path'], create_using=nx.DiGraph(), nodetype=None, data=[('weight', int)])
        elif db_info['mode'] == 'ceph':
            file_name = uuid.uuid1()
            print(file_name)
            cache_dir_path = '../../cache'
            file_cache_path = cache_dir_path + '/' + str(file_name)
            self.CephClient.download_file(save_file_name=file_cache_path,
                                          bucket_name=db_info['bucket'],
                                          key_name=db_info['path'])
            G = nx.read_edgelist(db_info['cache_path'], create_using=nx.DiGraph(), nodetype=None, data=[('weight', int)])
            os.remove(db_info['cache_path'])
        else:
            raise Exception('err mode')
        return G

    def _init_model(self):
        self.model_params = self.model_cfg['model_params']
        self.model = eval('{}(self.graph,**self.model_params)'.format(self.model_cfg['model_name']))

    def sink(self, df: pd.DataFrame, db_info: dict):
        """
        保存embedding
        """
        if db_info['sink_mode'] == 'local':
            df.to_csv(db_info['sink_path'], encoding='utf_8_sig', index=False)
        elif db_info['sink_mode'] == 'ceph':
            save_file_dir = '../../cache'
            bucket_name = self.recall_cfg['customer']
            emb_name = 'emb_{}-{}-{}-{}-{}.csv.{}'.format(self.recall_cfg['customer'],
                                                          self.recall_cfg['model'],
                                                          db_info['collection_name'],
                                                          str(self.emb_size),
                                                          db_info['version'],
                                                          str(time.strftime("%Y%m%d%H%M%S", time.localtime())))

            emb_md5_name = 'emb_{}-{}-{}-{}-{}.csv-tag'.format(self.recall_cfg['customer'],
                                                          self.recall_cfg['model'],
                                                          db_info['collection_name'],
                                                          str(self.emb_size),
                                                          db_info['version'])

            # 保存本地缓存
            emb_save_cache_file_path = save_file_dir + '/' + emb_name
            emb_md5_save_cache_file_path = save_file_dir + '/' + emb_md5_name

            df.to_csv(emb_save_cache_file_path, encoding='utf_8_sig', index=False)
            md5val = hashlib.md5(open(emb_save_cache_file_path, 'rb').read()).hexdigest()
            with open(emb_md5_save_cache_file_path, 'w') as f:
                data = md5val + " " + emb_name
                f.write(data)

            # 上传ceph
            emb_key_name = db_info['sink_dir_path'] + '/' + emb_name
            emb_md5_key_name = db_info['sink_dir_path'] + '/' + emb_md5_name
            ret = self.CephClient.upload_file(upload_file_name=emb_save_cache_file_path,
                                              bucket_name=bucket_name,
                                              key_name=emb_key_name)
            ret = self.CephClient.upload_file(upload_file_name=emb_md5_save_cache_file_path,
                                              bucket_name=bucket_name,
                                              key_name=emb_md5_key_name)
            os.remove(emb_save_cache_file_path)
            os.remove(emb_md5_save_cache_file_path)

    def fit(self):
        self.model.train(**self.model_cfg['train_params'])

    def save(self):
        db_info = self.recall_cfg['model_db_info']
        embeddings = self.model.get_embeddings()
        item_id = embeddings.keys()
        vector = embeddings.values()
        self.emb_size = len(list(vector)[0])
        vector = ['|'.join([str(j) for j in i]) for i in vector]
        data = {"item_id": item_id, "vector": vector}
        df = pd.DataFrame(data, columns=['item_id', 'vector'])
        self.sink(df, db_info)


if __name__ == '__main__':
    config = '../config/project.yaml'
    rt = RecallTrainer(config)
    rt.fit()
    rt.save()