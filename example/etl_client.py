# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : etl_client.py
# Time       ：2021/8/18 15:38
# Author     ：linxingliang
"""
import json
import grpc
import sys
sys.path.append('../')
from realtime_rec.protobuf import etl_engine_pb2, etl_engine_pb2_grpc
from realtime_rec.utils.common import read_config, get_feature_name_list


_HOST = '127.0.0.1'
_PORT = '19999'


def main():
    with grpc.insecure_channel("{}:{}".format(_HOST, _PORT)) as channel:
        client = etl_engine_pb2_grpc.ETLEngineStub(channel=channel)
        request_info = etl_engine_pb2.ItemETLRequestInfo()
        request_base_info = request_info.request_base_info
        request_base_info.customer_id = 'k11'
        request_base_info.scene_id = 'online'
        request_base_info.experiment_id = '001'
        response = client.UserETLRequest(request_info)
    print(response)


if __name__ == '__main__':
    main()