# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : gdbt_trainer.py
# Time       ：2021/10/8 15:51
# Author     ：aliang
"""

import pickle
# from realtime_rec.deepctr_rank_models import *
from deepctr.models import *
from rec.utils.common import read_config, get_feature_columns
import os
from tensorflow.keras.models import save_model
from rec.utils.connection import CephClient
from rec.metric.evaluate import evaluate_ctr
import nacos
import time
import hashlib
from rec.utils.common import gen_cfg_name, gen_global_cfg_name, get_gpu_num
from rec.utils.common import read_data, deepctr_get_cols_type, deepctr_get_model_cols_order
from rec.metric.evaluate import auroc
from tensorflow.python.keras.utils import multi_gpu_model


class RankTrainer(object):
    def __init__(self, config=None, customer_id=None, scene_id=None, experiment_id=None):
        cfg_info = [customer_id, scene_id, experiment_id]
        if isinstance(config, str):
            self.project_cfg = read_config(config)
            self.rank_cfg = read_config(self.project_cfg[gen_cfg_name('rank', cfg_info)])
            self.con_cfg = read_config(self.project_cfg[gen_global_cfg_name('connection', customer_id)])
            self.model_cfg = read_config(os.path.join('../config/ctr', self.rank_cfg['model'] + '.yaml'))
        elif isinstance(config, dict):
            self.rank_cfg = config[gen_cfg_name('rank', cfg_info)]
            self.con_cfg = config[gen_global_cfg_name('connection', customer_id)]
            self.model_cfg = config[self.rank_cfg['model']]
        else:
            self.autoNacos = nacos.AutoNacos()
            self.rank_cfg = self.autoNacos.get_config(gen_cfg_name('rank', cfg_info))
            self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))
            self.model_cfg = self.autoNacos.get_config(self.rank_cfg['model'])
        self.CephClient = CephClient(self.con_cfg)
        self.enc_dict = read_data(self.rank_cfg['enc_db_info'], ceph=self.CephClient)
        self.train_data = read_data(self.rank_cfg['sample_db_info'], ceph=self.CephClient)
        self._init_model()

    def _init_model(self):
        """
        初始化模型
        """
        self.params = self.model_cfg['params']
        self.cols_type = deepctr_get_cols_type(self.rank_cfg)
        self.cols_order = deepctr_get_model_cols_order(self.rank_cfg)
        self.linear_feature_columns = get_feature_columns(self.cols_type, self.enc_dict)
        self.dnn_feature_columns = get_feature_columns(self.cols_type, self.enc_dict)
        self.params['linear_feature_columns'] = self.linear_feature_columns
        self.params['dnn_feature_columns'] = self.dnn_feature_columns
        self.params['task'] = 'binary'
        self.model = eval('{}(**self.params)'.format(self.model_cfg['model_name']))
        gpu_num = get_gpu_num()
        if gpu_num > 1:
            self.model = multi_gpu_model(self.model, gpu_num)
        self.model.compile("adagrad", "binary_crossentropy", metrics=["binary_crossentropy"], )

    def execute(self):
        self.model.fit(self.train_data, self.train_data['label'],
                       batch_size=self.model_cfg['batch_size'],
                       epochs=self.model_cfg['n_epoch'],
                       verbose=2,
                       validation_split=0.2)

    def save_model(self):
        self.sink(db_info=self.rank_cfg['model_db_info'])

    def sink(self, db_info: dict):
        """
        保存embedding
        """
        update_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        model_name = 'model_{}-{}-{}.h5.{}'.format(self.rank_cfg['customer'],
                                                   self.rank_cfg['model'],
                                                   db_info['version'],
                                                   update_time)
        model_md5_name = 'model_{}-{}-{}.h5-tag'.format(self.rank_cfg['customer'],
                                                        self.rank_cfg['model'],
                                                        db_info['version'])
        enc_name = "enc_{}-{}.pkl.{}".format(self.rank_cfg['customer'],
                                             self.rank_cfg['model'],
                                             update_time)

        if db_info['sink_mode'] == 'local':

            model_path = db_info['sink_dir_path'] + '/' + model_name
            md5_path = db_info['sink_dir_path'] + '/' + model_md5_name
            enc_path = db_info['sink_dir_path'] + '/' + enc_name
            save_model(self.model, model_path)
            with open(enc_path, 'wb') as f:
                pickle.dump(self.enc_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

            model_md5 = hashlib.md5(open(model_path, 'rb').read()).hexdigest()
            enc_md5 = hashlib.md5(open(enc_path, 'rb').read()).hexdigest()
            with open(md5_path, 'w') as f:
                data = model_md5 + " " + model_name + '\n' + enc_md5 + enc_name
                f.write(data)

        elif db_info['sink_mode'] == 'ceph':
            save_file_dir = '../../cache'
            bucket_name = self.rank_cfg['customer']

            # 保存本地缓存
            model_save_cache_file_path = save_file_dir + '/' + model_name
            md5_save_cache_file_path = save_file_dir + '/' + model_md5_name
            enc_save_cache_file_path = save_file_dir + '/' + enc_name

            save_model(self.model, model_save_cache_file_path)
            with open(enc_save_cache_file_path, 'wb') as f:
                pickle.dump(self.enc_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

            model_md5 = hashlib.md5(open(model_save_cache_file_path, 'rb').read()).hexdigest()
            enc_md5 = hashlib.md5(open(enc_save_cache_file_path, 'rb').read()).hexdigest()
            with open(md5_save_cache_file_path, 'w') as f:
                data = model_md5 + " " + model_name + '\n' + enc_md5 + " " + enc_name
                f.write(data)

            # 上传ceph
            model_key_name = db_info['sink_dir_path'] + '/' + model_name
            model_md5_key_name = db_info['sink_dir_path'] + '/' + model_md5_name
            enc_key_name = db_info['sink_dir_path'] + '/' + enc_name
            ret = self.CephClient.upload_file(upload_file_name=model_save_cache_file_path,
                                              bucket_name=bucket_name,
                                              key_name=model_key_name)
            ret = self.CephClient.upload_file(upload_file_name=md5_save_cache_file_path,
                                              bucket_name=bucket_name,
                                              key_name=model_md5_key_name)
            ret = self.CephClient.upload_file(upload_file_name=enc_save_cache_file_path,
                                              bucket_name=bucket_name,
                                              key_name=enc_key_name)
            os.remove(model_save_cache_file_path)
            os.remove(md5_save_cache_file_path)
            os.remove(enc_save_cache_file_path)

    def evaluate(self, test_data):
        pred_ans = self.model.predict(test_data, batch_size=2560).reshape(-1)
        result = evaluate_ctr(test_data, pred_ans)
        return result


if __name__ == '__main__':
    rt = RankTrainer(customer_id='k11', scene_id='online', experiment_id='001')
    rt.execute()
    rt.save_model()