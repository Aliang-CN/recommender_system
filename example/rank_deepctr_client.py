# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : rank_deepctr_client.py
# Time       ：2021/9/3 15:18
# Author     ：linxingliang
"""
import grpc
import pandas as pd
import sys
sys.path.append('../')
from realtime_rec.protobuf import rank_engine_pb2
from realtime_rec.protobuf import rank_engine_pb2_grpc
from realtime_rec.utils.common import read_config, get_feature_name_list
from realtime_rec.utils.connection import Connection as Con
from realtime_rec.utils.common import deepctr_get_cols_order
import time

_HOST = '192.168.50.40'
_PORT = '19998'


def main():
    wide_table = pd.read_csv('../data/widetable_db/wide_table.csv', nrows=200)
    wide_table = wide_table.drop('label', 1)
    rank_cfg = read_config('../realtime_rec/config/online_rank.yaml')
    cols_order = deepctr_get_cols_order(rank_cfg)[:-1]
    wide_table = wide_table[cols_order]
    res = wide_table.values.tolist()

    request_data = ["&&".join([str(j) for j in i]) for i in res]
    print(request_data)
    with grpc.insecure_channel("{}:{}".format(_HOST, _PORT)) as channel:
        client = rank_engine_pb2_grpc.RankEngineStub(channel=channel)
        request_info = rank_engine_pb2.RequestInfo()
        request_info.RequestAlgorithm = 'deepfm'
        for s in request_data:
            request_item = request_info.RequestSample.add()
            request_item.FeatureList = s
        start = time.time()
        response = client.RankRequest(request_info)
        end = time.time()
        spend_time = end-start
        print(spend_time)
    print(response)


if __name__ == '__main__':
    main()