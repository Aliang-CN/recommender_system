# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : nearline_grpc.py
# Time       ：2023/9/7 15:21
# Author     ：aliang
"""
import json
import grpc
from concurrent import futures
import sys
sys.path.append('../../')
from rec.nearline import OLAPEngine, TextEmbeddingEngine
from rec.protobuf import nearline_engine_pb2, nearline_engine_pb2_grpc


class NearlineService(object):
    def __init__(self):
        pass

    def OLAPRequest(self, request, ctx):
        pipeline_id = request.request_base_info.pipeline_id
        config = request.request_base_info.config
        config = json.loads(config)
        self.OLAP_engine = OLAPEngine()
        self.OLAP_engine.run()
        response = nearline_engine_pb2.Response()
        response.response_info = 200
        return response

    def TextEmbeddingRequest(self, request, ctx):
        pipeline_id = request.request_base_info.pipeline_id
        config = request.request_base_info.config
        config = json.loads(config)
        self.text_embedding = TextEmbeddingEngine()
        self.text_embedding.run()
        response = nearline_engine_pb2.Response()
        response.response_info = 200
        return response


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = NearlineService()
    nearline_engine_pb2_grpc.add_NearlineEngineServicer_to_server(servicer, server)
    server.add_insecure_port('0.0.0.0:19997')
    server.start()
    server.wait_for_termination()
