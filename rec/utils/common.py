# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : common.py
# Time       ：2023/8/6 11:14
# Author     ：aliang
"""
import os
from io import BytesIO
import pandas as pd
import yaml
import pickle
import numpy as np
import importlib
from collections import defaultdict
from tensorflow.python.keras.preprocessing.sequence import pad_sequences
from tensorflow.python.client import device_lib


def read_config(config_path):
    with open(config_path, 'rb') as f:
        config = yaml.safe_load(f)
    return config


def get_feature_name_list(feature):
    # 获取特征名字
    feature_name_list = []
    feature_name_list.extend(feature.get('num_cols', []))
    feature_name_list.extend(feature.get('cate_cols', []))
    feature_name_list.extend(feature.get('multicate_cols', dict()).keys())
    return feature_name_list


def deepctr_get_cols_type(config):
    item_feature = config['item_feature']
    user_feature = config['user_feature']
    num_cols = item_feature.get('num_cols', []) + user_feature.get('num_cols', [])
    cate_cols = item_feature.get('cate_cols', []) + user_feature.get('cate_cols', [])
    multicate_cols = {**item_feature.get('multicate_cols', dict()), **user_feature.get('multicate_cols', dict())}
    cols_type = {'num_cols': num_cols, 'cate_cols': cate_cols, 'multicate_cols': multicate_cols}
    return cols_type


def deepctr_get_model_cols_order(config):
    """
    获取模型的输入
    """
    item_feature = config['item_feature']
    user_feature = config['user_feature']
    num_cols = item_feature.get('num_cols', []) + user_feature.get('num_cols', [])
    cate_cols = item_feature.get('cate_cols', []) + user_feature.get('cate_cols', [])
    multicate_cols = {**item_feature.get('multicate_cols', dict()), **user_feature.get('multicate_cols', dict())}
    model_cols_order = num_cols + cate_cols + list(multicate_cols.keys())
    return model_cols_order


def deepctr_get_cols_order(config):
    """
    获取请求的输入
    """
    item_feature = config['item_feature']
    user_feature = config['user_feature']
    user_feature_name = get_feature_name_list(user_feature)
    item_feature_name = get_feature_name_list(item_feature)
    cols_order = user_feature_name + item_feature_name + ['label']
    return cols_order


def deepctr_feature_encode(data: pd.DataFrame, cols_type: dict, enc_dict: dict):
    data_result_dict = {}

    def _mutilcat_encode(x, col_enc_dict):
        key_ans = x.split("|")
        return [col_enc_dict.get([i], col_enc_dict['isnan']) for i in key_ans]

    def _cat_encode(x, col_enc_dict):
        return col_enc_dict.get(x, col_enc_dict['isnan'])

    def _normalizer(x, col_enc_dict):
        if x > col_enc_dict['max']:
            return 1
        elif x < col_enc_dict['min']:
            return 0
        else:
            return (x - col_enc_dict['min'])/(col_enc_dict['max'] - col_enc_dict['min'])

    for col in data.columns:
        if col in cols_type['num_cols']:
            col_data = data[col].astype(float)
            col_data = col_data.map(lambda x: _normalizer(x, enc_dict[col]))
            data_result_dict[col] = col_data
        elif col in cols_type['cate_cols']:
            col_data = data[col].astype(str)
            col_data = col_data.map(lambda x: _cat_encode(x, enc_dict[col]))  # 把里面的值用编码代替
            data_result_dict[col] = col_data
        elif col in cols_type['multicate_cols'].keys():
            col_data = list(map(lambda x: _mutilcat_encode(x, enc_dict[col]), data[col].values))
            col_data = pad_sequences(col_data, maxlen=cols_type['multicate_cols'][col], padding='post', )
            data_result_dict[col] = col_data
        else:
            continue

    if 'label' in data.columns:
        label = data['label'].tolist()
        data_result_dict['label'] = label
    return data_result_dict


def deepctr_gen_feature_encode_dict(data, config):
    item_feature = config['item_feature']
    user_feature = config['user_feature']
    num_cols = item_feature.get('num_cols', []) + user_feature.get('num_cols', [])
    cate_cols = item_feature.get('cate_cols', []) + user_feature.get('cate_cols', [])
    multicate_cols = {**item_feature.get('multicate_cols', dict()), **user_feature.get('multicate_cols', dict())}
    enc_dict = defaultdict(dict)
    for col in data.columns:
        if col in num_cols:
            num_max = np.max(data[col].tolist())
            num_min = np.min(data[col].tolist())
            col_feat_dict = {}
            col_feat_dict['max'] = num_max
            col_feat_dict['min'] = num_min
            enc_dict[col] = col_feat_dict
        elif col in cate_cols:
            data[col] = data[col].astype(str)
            uniques = data[col].unique().tolist()
            if 'isnan' not in uniques:
                uniques = ['isnan'] + uniques
            col_feat_dict = dict(zip(uniques, range(len(uniques))))
            enc_dict[col] = col_feat_dict
        elif col in multicate_cols.keys():
            uniques = []
            df_list = data[col].values
            for i in df_list:
                i = i.split('|')
                uniques.extend(i)
            uniques = list(set(uniques))
            if 'isnan' not in uniques:
                uniques = ['isnan'] + uniques
            uniques = list(set(uniques))
            col_feat_dict = dict(zip(uniques, range(len(uniques))))
            enc_dict[col] = col_feat_dict
        else:
            continue
    return enc_dict


def get_feature_columns(feature_cfg, enc_dict):
    """
    生成deepctr对应的列类
    """
    from deepctr.feature_column import DenseFeat, SparseFeat, VarLenSparseFeat
    if 'num_cols' in feature_cfg.keys():
        dense_feature_colums = [DenseFeat(feat, 1, ) for feat in feature_cfg['num_cols']]
    else:
        dense_feature_colums = []
    if 'cate_cols' in feature_cfg.keys():
        sparse_feature_colums = [SparseFeat(feat, len(enc_dict[feat]),
                                            embedding_dim=4) for feat in feature_cfg['cate_cols']]
    else:
        sparse_feature_colums = []
    if 'multicate_cols' in feature_cfg.keys():
        varlen_feature_columns = [VarLenSparseFeat(SparseFeat(feat, vocabulary_size=len(enc_dict[feat]), embedding_dim=4),
                                                   maxlen=max_len, combiner='mean', weight_name=None) for feat, max_len in feature_cfg['multicate_cols'].items()]
    else:
        varlen_feature_columns = []
    feature_colums = dense_feature_colums + sparse_feature_colums + varlen_feature_columns
    return feature_colums


def get_feature_columns_torch(feature_cfg, enc_dict):
    """
    生成deepctr对应的列类
    """
    from deepctr_torch.inputs import DenseFeat, SparseFeat, VarLenSparseFeat
    if 'num_cols' in feature_cfg.keys():
        dense_feature_colums = [DenseFeat(feat, 1, ) for feat in feature_cfg['num_cols']]
    else:
        dense_feature_colums = []
    if 'cate_cols' in feature_cfg.keys():
        sparse_feature_colums = [SparseFeat(feat, len(enc_dict[feat]),
                                            embedding_dim=4) for feat in feature_cfg['cate_cols']]
    else:
        sparse_feature_colums = []
    if 'multicate_cols' in feature_cfg.keys():
        varlen_feature_columns = [VarLenSparseFeat(SparseFeat(feat, vocabulary_size=len(enc_dict[feat]), embedding_dim=4),
                                                   maxlen=max_len, combiner='mean') for feat, max_len in feature_cfg['multicate_cols'].items()]
    else:
        varlen_feature_columns = []
    feature_colums = dense_feature_colums + sparse_feature_colums + varlen_feature_columns
    return feature_colums


def shuffle_data(xi, xv, y):
    rng_state = np.random.get_state()
    np.random.shuffle(xi)
    np.random.set_state(rng_state)
    np.random.shuffle(xv)
    np.random.set_state(rng_state)
    np.random.shuffle(y)
    return xi, xv, y


def split_data(xi, xv, y):
    train_xi = xi[:int(0.8*len(xi))]
    train_xv = xv[:int(0.8*len(xv))]
    train_y = y[:int(0.8*len(y))]

    test_xi = xi[int(0.8*len(xi)):]
    test_xv = xv[int(0.8*len(xv)):]
    test_y = y[int(0.8*len(y)):]

    return train_xi, train_xv, train_y, test_xi, test_xv, test_y


def load_rank_model(model_name):
    model_filename = "realtime_rec.models.rank_models." + model_name
    modellib = importlib.import_module(model_filename)
    model = None
    for name, cls in modellib.__dict__.items():
        if name.lower() == 'model':
            model = cls
    return model


def load_recall_model(model_name):
    model_filename = "realtime_rec.models.recall_models." + model_name
    print(model_filename)
    modellib = importlib.import_module(model_filename)
    model = None
    for name, cls in modellib.__dict__.items():
        if name.lower() == 'model':
            model = cls
    return model


def sink(data, db_info, ceph=None):
    if db_info['mode'] == 'local':
        save_path = db_info['path']
    elif db_info['mode'] == 'ceph':
        save_path = db_info['cache_path']
    else:
        raise Exception('mode is not supported')

    dir_path = os.path.dirname(save_path)
    if not os.path.exists(dir_path):
        print(dir_path)
        os.makedirs(dir_path)

    if isinstance(data, dict):
        with open(save_path, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    elif isinstance(data, pd.DataFrame):
        data.to_csv(save_path,
                    sep=db_info['sep'] if 'sep' in db_info.keys() else ',',
                    header=db_info['header'] if 'header' in db_info.keys() else True,
                    encoding='utf_8_sig', index=False)
    else:
        raise Exception('File format is not supported')

    if db_info['mode'] == 'ceph':
        ret = ceph.upload_file(upload_file_name=save_path,
                                     bucket_name=db_info['bucket'],
                                     key_name=db_info['path'])
    return 0


def read_data(db_info, con=None, ceph=None):
    if db_info['mode'] == 'local':
        source_path = db_info['path']
        file_format = os.path.basename(source_path).split(".")[-1]
        if file_format == 'pkl':
            with open(source_path, 'rb') as f:
                data = pickle.load(f)
        elif file_format == 'csv':
            data = pd.read_csv(source_path, sep=db_info['sep'] if 'sep' in db_info.keys() else ',')
        else:
            raise Exception('{} is not supported'.format(file_format))
    elif db_info['mode'] == 'mysql':
        sql = db_info['path']
        data = pd.read_sql(sql, con)
    elif db_info['mode'] == 'ceph':
        source_path = db_info['path']
        file_format = os.path.basename(source_path).split(".")[-1]
        if file_format == 'pkl':
            resp = ceph._conn_s3.get_object(Bucket=db_info['bucket'], Key=source_path)
            data = pickle.load(BytesIO(resp['Body']._raw_stream.data))
        elif file_format == 'csv':
            data_list = ceph.get_files_list(bucket_name=db_info['bucket'])
            if source_path not in data_list:
                raise Exception('ceph not exit {}'.format(source_path))
            url = ceph.generate_presigned_url(bucket_name=db_info['bucket'], key_name=source_path)
            data = pd.read_csv(url, sep=db_info['sep'] if 'sep' in db_info.keys() else ',')
        else:
            raise Exception('{} is not supported'.format(file_format))
    else:
        raise Exception('{} is not supported'.format(db_info['mode']))
    return data


def gen_cfg_name(func: str, info: list):
    cfg_name = "_".join(info)
    cfg_name = cfg_name + '_' + func
    return cfg_name


def gen_global_cfg_name(func: str, customer_id):
    global_cfg_name = "_".join([customer_id, func])
    return global_cfg_name


def get_gpu_num():
    device_info = device_lib.list_local_devices()
    num_gpu = len([device for device in device_info if device.device_type=='GPU'])
    return num_gpu