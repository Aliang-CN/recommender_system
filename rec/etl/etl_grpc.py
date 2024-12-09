# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : rank_data_process_grpc.py
# Time       ：2021/8/18 13:43
# Author     ：aliang
"""
import sys

sys.path.append('../../')

import grpc
from concurrent import futures
from rec.protobuf import etl_engine_pb2, etl_engine_pb2_grpc
from rec.etl.etl_engine import ETLEngine


class ETLService(object):
    def __init__(self, ):
        pass

    def ItemETLRequest(self, request, ctx):
        print('ItemETLRequest', request)
        customer_id = request.request_base_info.customer_id
        project_id = request.request_base_info.project_id
        scene_id = request.request_base_info.scene_id
        ETL = ETLEngine(customer_id=customer_id, project_id=project_id, scene_id=scene_id)
        ETL.deal_with_item_data()
        del ETL
        response = etl_engine_pb2.Response()
        response.response_info = 200
        return response

    def UserETLRequest(self, request, ctx):
        print('UserETLRequest', request)
        customer_id = request.request_base_info.customer_id
        project_id = request.request_base_info.project_id
        scene_id = request.request_base_info.scene_id
        ETL = ETLEngine(customer_id=customer_id, project_id=project_id, scene_id=scene_id)
        ETL.deal_with_user_data()
        del ETL
        response = etl_engine_pb2.Response()
        response.response_info = 200
        return response

    def BehaviorETLRequest(self, request, ctx):
        print('BehaviorETLRequest', request)
        customer_id = request.request_base_info.customer_id
        project_id = request.request_base_info.project_id
        scene_id = request.request_base_info.scene_id
        ETL = ETLEngine(customer_id=customer_id, project_id=project_id, scene_id=scene_id)
        ETL.deal_with_behavior_data()
        del ETL
        response = etl_engine_pb2.Response()
        response.response_info = 200
        return response

    def JoinRequest(self, request, cxt):
        print('JoinRequest', request)
        customer_id = request.request_base_info.customer_id
        project_id = request.request_base_info.project_id
        scene_id = request.request_base_info.scene_id
        ETL = ETLEngine(customer_id=customer_id, project_id=project_id, scene_id=scene_id)
        ETL.join_data()
        del ETL
        response = etl_engine_pb2.Response()
        response.response_info = 200
        return response


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = ETLService()
    etl_engine_pb2_grpc.add_ETLEngineServicer_to_server(servicer, server)
    server.add_insecure_port('0.0.0.0:19999')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    main()
