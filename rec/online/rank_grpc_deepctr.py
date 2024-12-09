# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : rank_grpc_deepctr.py
# Time       ：2023/8/27 11:09
# Author     ：aliang
"""

import grpc
from concurrent import futures
import sys
sys.path.append('../../')
from rec.protobuf import rank_engine_pb2
from rec.protobuf import rank_engine_pb2_grpc
from rec.online.rank_engine_deepctr import RankEngine
# from realtime_rec.online.rank_engine_deepctr_bak import RankEngine
import time


class RankServicer():
    def __init__(self, customer_id=None, project_id=None, scene_id=None):
        self.RE = RankEngine(customer_id=customer_id, project_id=project_id, scene_id=scene_id)

    def RankRequest(self, request, ctx):             # 请求，上下文
        sample_list = request.RequestSample
        sample_list = [s.FeatureList for s in sample_list]
        start_time = time.time()
        sample_list = [featurelist.split('&&') for featurelist in sample_list]
        scores = self.RE.predict(sample_list)
        end_time = time.time()
        print('总时长', end_time-start_time)
        response = rank_engine_pb2.Response()
        response.ResponseInfo = 0
        if isinstance(scores, list):
            for score in scores:
                response_value = response.ScoreList.add()
                response_value.value = score
        else:
            response_value = response.ScoreList.add()
            response_value.value = scores
        return response

    def UpdateModel(self, request, ctx):
        customer_id = request.request_base_info.customer_id
        project_id = request.request_base_info.project_id
        scene_id = request.request_base_info.scene_id
        self.RE = RankEngine(customer_id=customer_id, project_id=project_id, scene_id=scene_id)
        response = rank_engine_pb2.Response()
        response.ResponseInfo = 200
        return response


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = RankServicer()
    rank_engine_pb2_grpc.add_RankEngineServicer_to_server(servicer, server)
    server.add_insecure_port('0.0.0.0:19998')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    main()