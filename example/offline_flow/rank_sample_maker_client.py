# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : rank_sample_maker_client.py
# Time       ：2021/9/2 13:49
# Author     ：aliang
"""

import grpc
import json
import sys
sys.path.append('../../')
from rec.protobuf import offline_train_pb2, offline_train_pb2_grpc

_HOST = '127.0.0.1'
_PORT = '19998'


def main(argv):
    with grpc.insecure_channel("{}:{}".format(_HOST, _PORT)) as channel:
        client = offline_train_pb2_grpc.OfflineEngineStub(channel=channel)
        request_info = offline_train_pb2.RankSampleMakerRequestInfo()
        request_base_info = request_info.request_base_info
        request_base_info.pipeline_id = argv[1]
        request_base_info.config = argv[2]
        response = client.RankSampleMakerRequest(request_info)
    print(response)


if __name__ == '__main__':
    print("RankSampleMakerRequest start")
    config = {}
    config = json.dumps(config)
    argv = []
    argv.append('00')
    argv.append('001')
    argv.append(config)
    main(argv)