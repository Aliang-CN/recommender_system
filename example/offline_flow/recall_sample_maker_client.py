# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : recall_sample_maker_client.py
# Time       ：2021/9/2 13:49
# Author     ：linxingliang
"""

import sys
import grpc
import json
import sys
sys.path.append('../../')
from realtime_rec.protobuf import offline_train_pb2, offline_train_pb2_grpc
from realtime_rec.utils.common import read_config
_HOST = '192.168.50.21'
_PORT = '19998'


def main(argv):
    with grpc.insecure_channel("{}:{}".format(_HOST, _PORT)) as channel:
        client = offline_train_pb2_grpc.OfflineEngineStub(channel=channel)
        request_info = offline_train_pb2.RecallSampleMakerRequestInfo()
        request_base_info = request_info.request_base_info
        request_base_info.pipeline_id = argv[1]
        request_base_info.config = argv[2]
        response = client.RecallSampleMakerRequest(request_info)
    print(response)


if __name__ == '__main__':
    print("RecallSampleMakerRequest start")
    # config = r'D:\python_project\deepwisdom\AutoRec-Realtime\realtime_rec\config\project.yaml'
    # project_cfg = read_config(config)
    # recall_cfg = read_config(project_cfg['online_recall'])
    # con_cfg = read_config(project_cfg['connection'])
    # config = {'online_recall': recall_cfg, 'connection': con_cfg}
    config = {}
    config = json.dumps(config)
    argv = []
    argv.append('00')
    argv.append('001')
    argv.append(config)
    main(argv)