# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : rank_trainer_client.py
# Time       ：2021/9/2 13:50
# Author     ：aliang
"""

import sys
import grpc
import json
import sys
sys.path.append('../../')
from rec.utils.common import read_config
from rec.protobuf import offline_train_pb2, offline_train_pb2_grpc

_HOST = 'localhost'
_PORT = '19998'


def main(argv):
    with grpc.insecure_channel("{}:{}".format(_HOST, _PORT)) as channel:
        client = offline_train_pb2_grpc.OfflineEngineStub(channel=channel)
        request_info = offline_train_pb2.RankTrainerRequestInfo()
        request_base_info = request_info.request_base_info
        request_base_info.pipeline_id = argv[1]
        request_base_info.config = argv[2]
        response = client.RankTrainerRequest(request_info)
    print(response)


if __name__ == '__main__':
    print("RankTrainerRequest start")
    config = {}
    config = json.dumps(config)
    argv = []
    argv.append('00')
    argv.append('001')
    argv.append(config)
    main(argv)