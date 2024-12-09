# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : recall_infer.py
# Time       ：2023/8/10 16:26
# Author     ：aliang
"""

from rec.utils.common import read_config
from rec.utils.connection import Connection as Con
import grpc
from rec.protobuf import vec_milvus_engine_pb2
from rec.protobuf import vec_milvus_engine_pb2_grpc
import random


class RecallEngine(object):
    def __init__(self, config_path):
        self.config = read_config(config_path=config_path)  # 读取项目配置表
        self.recall_config = read_config(config_path=self.config['online_recall_path'])  # 在线召回配置
        self.con_config = read_config(self.config['connection_path'])
        self.recall_con_config = self.con_config['recall']  # 召回连接配置
        self.Con = Con(self.config['connection_path'])
        self.channel = self._init_channel()
        self.redis_con = self.Con.redis_con()

    def _init_channel(self):
        channel = grpc.insecure_channel("{}:{}".format(str(self.recall_con_config['vecsearch']['host']),
                                                       str(self.recall_con_config['vecsearch']['host'])))
        return channel

    def vec_recall(self, user):
        # 获取用户最近行为
        request_items = self.redis_con.lrange('hist'+user, 0, self.recall_config['vec_hist_num'])  # 列表
        client = vec_milvus_engine_pb2_grpc.VecMilvusEngineStub(channel=self.channel)
        vec_request_info = vec_milvus_engine_pb2.VecRequestInfo()
        vec_request_info.recall_topk = 10
        vec_request_info.request_algorithm = self.recall_config['recall_algorithm']

        for item in request_items:
            request_item = vec_request_info.request_item_list.add()
            request_item.item_id = item
        response = client.VecSearch(vec_request_info)
        return response

    def hotitems_recall(self, user):
        # 获取热门item全局表
        hot_items = self.redis_con.lrange(self.recall_config['hot_items_name'], 0, -1)
        hot_items = random.sample(hot_items, k=self.recall_config['hot_sample_num'])
        return hot_items

    def newitem_recall(self, user):
        # 获取新item全局表
        new_items = self.redis_con.lrange(self.recall_config['hot_items_name'], 0, -1)
        new_items = random.sample(new_items, k=self.recall_config['hot_sample_num'])
        return new_items

    def colditem_recall(self, user):
        # 获取全局冷门item全局表
        new_items = self.redis_con.lrange(self.recall_config['hot_items_name'], 0, -1)
        new_items = random.sample(new_items, k=self.recall_config['hot_sample_num'])
        return new_items

    def tag_recall(self, user):
        # 获取用户喜欢标签
        user_like_tags = self.redis_con.hmget(user, *self.recall_config['tag_recall_name'])
        user_like_tags = [i.split('|') for i in user_like_tags]
        all_items = []
        for tag in user_like_tags:
            items = self.redis_con.lrange(self.recall_config[tag], 0, -1)
            all_items.append(items)
        all_items = random.sample(all_items, k=self.recall_config['tag_sample_num'])
        return all_items

    def recall_pipeline(self, user):
        recall_collction = {}
        for recall_source in self.recall_config["recall_source"]:
            recall_result = getattr(self, recall_source)(user)
            recall_collction[recall_source] = recall_result
        return recall_collction


if __name__ == '__main__':
    config_path = '../config/project.yaml'
    recall_engine = RecallEngine(config_path)
    user = '0001f641-3e09-4b56-afae-fec8bb946381'
    recall_engine.recall_pipeline(user)
