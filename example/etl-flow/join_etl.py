# !/usr/bin/env python
# -*-coding:utf-8 -*-

import sys
import time

import grpc

from rec.protobuf import etl_engine_pb2, etl_engine_pb2_grpc

_HOST = '127.0.0.1'
_PORT = '19999'


def join_etl(argv):
    print("join-etl start")
    with grpc.insecure_channel("{}:{}".format(_HOST, _PORT)) as channel:
        client = etl_engine_pb2_grpc.ETLEngineStub(channel=channel)
        request_info = etl_engine_pb2.JoinRequestInfo()
        request_base_info = request_info.request_base_info
        request_base_info.pipeline_id = '1'
        request_base_info.config = '2'
        response = client.JoinRequest(request_info)
    print("join-etl end")
    print(response)


if __name__ == '__main__':
    join_etl(sys.argv)
