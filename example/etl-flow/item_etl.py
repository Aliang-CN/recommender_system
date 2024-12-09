# !/usr/bin/env python
# -*-coding:utf-8 -*-

import sys
import grpc

from rec.protobuf import etl_engine_pb2, etl_engine_pb2_grpc

_HOST = 'localhost'
_PORT = '19999'


def item_etl(argv):
    print("item-etl start")
    with grpc.insecure_channel("{}:{}".format(_HOST, _PORT)) as channel:
        client = etl_engine_pb2_grpc.ETLEngineStub(channel=channel)
        request_info = etl_engine_pb2.ItemETLRequestInfo()
        request_base_info = request_info.request_base_info
        request_base_info.pipeline_id = argv[1]
        request_base_info.config = argv[2]
        response = client.ItemETLRequest(request_info)
    print("item-etl end")
    print(response)


if __name__ == '__main__':
    item_etl(sys.argv)

