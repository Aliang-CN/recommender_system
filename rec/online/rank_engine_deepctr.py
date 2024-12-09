# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : rank_deepctr_engine.py.py
# Time       ：2021/8/26 11:21
# Author     ：aliang
"""

import pandas as pd
import tensorflow as tf
import os
import pickle
import numpy as np
from deepctr.layers import custom_objects
from tensorflow.keras.models import load_model
import nacos
from rec.utils.connection import Connection as Con
from rec.utils.connection import CephClient
from rec.utils.common import deepctr_feature_encode, deepctr_get_cols_order, deepctr_get_cols_type
from rec.utils.common import gen_cfg_name, gen_global_cfg_name
import time
import copy


class LiteModel:
    @classmethod
    def from_file(cls, model_path):
        return LiteModel(tf.lite.Interpreter(model_path=model_path))
    @classmethod
    def from_keras_model(cls, kmodel, custom_objects=None):
        converter = tf.lite.TFLiteConverter.from_keras_model_file(kmodel, custom_objects=custom_objects)
        tflite_model = converter.convert()
        return LiteModel(tf.lite.Interpreter(model_content=tflite_model))

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.interpreter.allocate_tensors()
        input_det = self.interpreter.get_input_details()
        output_det = self.interpreter.get_output_details()[0]
        self.input_index_dict = {i['name']: i['index'] for i in input_det}
        self.input_shape_dict = {i['name']: i['shape'] for i in input_det}
        self.input_dtype_dict = {i['name']: i['dtype'] for i in input_det}

        self.output_index = output_det["index"]
        self.output_shape = output_det["shape"]
        self.output_dtype = output_det["dtype"]

    def predict(self, inp, interpreter):
        """ Like predict(), but only for a single record. The input data can be a Python list. """
        count = len(inp['goods_sn'])
        print('num_item', count)
        out = np.zeros((count, self.output_shape[1]), dtype=self.output_dtype)
        inp = {k: np.expand_dims(np.expand_dims(np.array(vs, dtype=self.input_dtype_dict[k]), axis=1), axis=1) for k, vs in inp.items()}
        for i in range(count):
            for k, vs in inp.items():
                #input_tensor_z = tf.convert_to_tensor(vs[i], np.float32)
                #interpreter.set_tensor(self.input_index_dict[k], input_tensor_z )

                interpreter.set_tensor(self.input_index_dict[k], vs[i])


            interpreter.invoke()
            o = interpreter.get_tensor(self.output_index)
            #o = interpreter.tensor(self.output_index)
            #out[i] = copy.copy(o())
            out[i] = o

        return out

    def predict_single(self, inp):
        for k, vs in inp.items():
            v = np.array([vs[i]], dtype=self.input_dtype_dict[k])
            v = np.expand_dims(v, axis=0)
            self.interpreter.set_tensor(self.input_index_dict[k], v)
        self.interpreter.invoke()
        out = self.interpreter.get_tensor(self.output_index)
        return out


class RankEngine(object):
    def __init__(self, customer_id=None, project_id=None, scene_id=None):
        """
        1、获取配置表
        2、获取编码字典
        """
        cfg_info = [customer_id, project_id, scene_id]
        self.autoNacos = nacos.AutoNacos()
        self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))
        self.rank_cfg = self.autoNacos.get_config(gen_cfg_name('rank', cfg_info))
        self.model_cfg = self.autoNacos.get_config(self.rank_cfg['model'])

        self.CephClient = CephClient(self.con_cfg)
        self.cols_order = deepctr_get_cols_order(self.rank_cfg)[:-1]
        self.cols_type = deepctr_get_cols_type(self.rank_cfg)
        self.Con = Con(self.con_cfg)
        self.session = tf.Session()
        self.graph = tf.get_default_graph()
        self.enc_dict, self.model = self.load()

    def load(self):
        save_file_dir = '../../cache'
        bucket_name = self.rank_cfg['customer']
        model_md5_name = 'model_{}-{}-{}.h5-tag'.format(self.rank_cfg['customer'],
                                                        self.rank_cfg['model'],
                                                        self.rank_cfg['model_db_info']['version'])
        md5_key_name = self.rank_cfg['model_db_info']['sink_dir_path'] + '/' + model_md5_name
        md5_save_cache_file_path = save_file_dir + '/' + model_md5_name
        resp = self.CephClient.download_file(save_file_name=md5_save_cache_file_path,
                                             bucket_name=bucket_name,
                                             key_name=md5_key_name,
                                             always_overwrite=True)
        with open(md5_save_cache_file_path, 'r') as f:
            md5 = f.readlines()
        model_name = md5[0].rstrip().split(' ')[1]
        enc_name = md5[1].rstrip().split(' ')[1]
        model_key_name = self.rank_cfg['model_db_info']['sink_dir_path'] + '/' + model_name
        enc_key_name = self.rank_cfg['model_db_info']['sink_dir_path'] + '/' + enc_name
        model_save_cache_file_path = save_file_dir + '/' + model_name
        enc_save_cache_file_path = save_file_dir + '/' + enc_name
        resp = self.CephClient.download_file(save_file_name=model_save_cache_file_path,
                                             bucket_name=bucket_name,
                                             key_name=model_key_name,
                                             always_overwrite=True)
        resp = self.CephClient.download_file(save_file_name=enc_save_cache_file_path,
                                             bucket_name=bucket_name,
                                             key_name=enc_key_name,
                                             always_overwrite=True)
        with open(enc_save_cache_file_path, 'rb') as f:
            enc_dict = pickle.load(f)
        # with self.graph.as_default():
        #     with self.session.as_default():
        #         model = load_model(model_save_cache_file_path, custom_objects)
        model = LiteModel.from_keras_model(model_save_cache_file_path, custom_objects)
        os.remove(model_save_cache_file_path)
        os.remove(enc_save_cache_file_path)
        return enc_dict, model

    def _encode(self, request_info):
        data = pd.DataFrame(request_info)
        data.columns = self.cols_order
        input_data = deepctr_feature_encode(data, self.cols_type, self.enc_dict)
        return input_data

    def predict(self, request_info):
        start_time = time.time()
        input_data = self._encode(request_info)
        end_time = time.time()
        print('样本构建时长', end_time-start_time)
        start_time = time.time()
        predictions = self.model.predict(input_data, self.model.interpreter)
        end_time = time.time()
        print('推理时长', end_time-start_time)
        predictions = np.squeeze(predictions)
        predictions = predictions.tolist()
        return predictions


if __name__ == '__main__':
     re = RankEngine()
     print('done')
