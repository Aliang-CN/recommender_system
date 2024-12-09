# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : offline_grpc.py
# Time       ：2023/9/2 10:52
# Author     ：aliang
"""

import grpc
from concurrent import futures
import sys
sys.path.append('../../')
from rec.offline import RecallTrainer, RecallSampleMaker, RankTrainer, RankSampleMaker
from rec.protobuf import offline_engine_pb2, offline_engine_pb2_grpc


class OfflineService(object):
    def RankSampleMakerRequest(self, request, ctx):
        print('rank sample maker request')
        customer_id = request.request_base_info.customer_id
        project_id = request.request_base_info.project_id
        scene_id = request.request_base_info.scene_id
        rank_sample_maker = RankSampleMaker(customer_id=customer_id,
                                                 project_id=project_id,
                                                 scene_id=scene_id,)
        rank_sample_maker.transform()
        del rank_sample_maker
        response = offline_engine_pb2.Response()
        response.response_info = 200
        return response

    def RankTrainerRequest(self, request, ctx):
        print('rank trainer request')
        customer_id = request.request_base_info.customer_id
        project_id = request.request_base_info.project_id
        scene_id = request.request_base_info.scene_id
        rank_trainer = RankTrainer(customer_id=customer_id,
                                        project_id=project_id,
                                        scene_id=scene_id)
        rank_trainer.execute()
        rank_trainer.save_model()
        del rank_trainer
        response = offline_engine_pb2.Response()
        response.response_info = 200
        return response

    def RecallSampleMakerRequest(self, request, ctx):
        print('recall sample maker request')
        customer_id = request.request_base_info.customer_id
        project_id = request.request_base_info.project_id
        scene_id = request.request_base_info.scene_id
        recall_sample_maker = RecallSampleMaker(customer_id=customer_id,
                                                     project_id=project_id,
                                                     scene_id=scene_id,)
        recall_sample_maker.transform()
        del recall_sample_maker
        response = offline_engine_pb2.Response()
        response.response_info = 200
        return response

    def RecallTrainerRequest(self, request, ctx):
        print('recall trainer request')
        customer_id = request.request_base_info.customer_id
        project_id = request.request_base_info.project_id
        scene_id = request.request_base_info.scene_id
        recall_trainer = RecallTrainer(customer_id=customer_id,
                                            project_id=project_id,
                                            scene_id=scene_id,)
        recall_trainer.fit()
        recall_trainer.save()
        del recall_trainer
        response = offline_engine_pb2.Response()
        response.response_info = 200
        return response


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = OfflineService()
    offline_engine_pb2_grpc.add_OfflineEngineServicer_to_server(servicer, server)
    server.add_insecure_port('0.0.0.0:19997')
    server.start()
    server.wait_for_termination()