# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : clien.py
# Time       ：2021/8/12 20:39
# Author     ：linxingliang
"""


import grpc
import pandas as pd
import numpy as np
import sys
sys.path.append('../')
from realtime_rec.protobuf import rank_engine_pb2
from realtime_rec.protobuf import rank_engine_pb2_grpc
from realtime_rec.utils.common import read_config, get_feature_name_list
from realtime_rec.utils.connection import Connection as Con
import time

_HOST = '127.0.0.1'
_PORT = '19998'


def main():
    offline_config = read_config('../realtime_rec/config/offline_rank.yaml')
    user_feature = offline_config['user_feature']
    item_feature = offline_config['item_feature']
    user_feature_name = get_feature_name_list(user_feature)
    item_feature_name = get_feature_name_list(item_feature)

    redis_con = Con('../realtime_rec/config/connection.yaml').redis_con()
    pipe = redis_con.pipeline(transaction=True)

    spend_collector = []
    for i in range(1):
        # start = time.time()
        user_id = 'e5542306-56b5-4b0d-951d-2a8f23150292'
        item_ids = ['p7700110', 'p17076424', 'p16718843', 'p16696303', 'p1479502']

        user_profile = redis_con.hmget(user_id, user_feature_name)
        for item_id in item_ids:
            pipe.hmget(item_id, item_feature_name)
        item_profile = pipe.execute()
        request_data = [u + i for u, i in zip([user_profile]*len(item_profile), item_profile)]
        request_data = ["&&".join([str(j) for j in i]) for i in request_data]
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
        spend = end - start
        spend_collector.append(spend)
    print(spend_collector)
    mean_spend = np.mean(spend_collector)
    print(mean_spend)


if __name__ == '__main__':
    main()