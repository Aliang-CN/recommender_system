# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : sentence_embedding.py
# Time       ：2023/8/25 19:11
# Author     ：aliang
"""
import nacos
import grpc
import pandas as pd
from realtime_rec.utils.common import read_data, read_config
from sentence_transformers import SentenceTransformer
from realtime_rec.protobuf import vector_engine_pb2, vector_engine_pb2_grpc
from itertools import islice
from realtime_rec.utils.connection import Connection as Con
from realtime_rec.utils.common import read_config, gen_cfg_name, gen_global_cfg_name


class TextEmbeddingEngine(object):
    def __init__(self, nacos_file=None, customer_id=None):
        self.autoNacos = nacos.AutoNacos(nacos_file=nacos_file)
        self.text_embedding_cfg = self.autoNacos.get_config('text_embedding')
        self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))
        self.model = SentenceTransformer('distiluse-base-multilingual-cased-v1')

    def gen_embedding(self, texts):
        embeddings = self.model.encode(texts)
        return embeddings

    def write_to_engine(self, embedding_dict: dict, db_info: dict):
        with grpc.insecure_channel("{}:{}".format(db_info['host'], db_info['port'])) as channel:
            client = vector_engine_pb2_grpc.VecEngineServiceStub(channel=channel)
            request_info = vector_engine_pb2.UpdateVectorRequest()
            request_info.Dimension = len(list(embedding_dict.values())[0])
            request_info.Collection = db_info['collection_name']
            for item_id, vector in embedding_dict.items():
                embeddinginfos = request_info.EmbInfos.add()
                embeddinginfos.ItemId = str(item_id)
                for v in vector:
                    embeddinginfos.EmbVals.append(v)
            response = client.DoUpdateVector(request_info, timeout=30000)
        return response

    def chunks(self, data, SIZE=20):
        it = iter(data)
        for i in range(0, len(data), SIZE):
            yield {k: data[k] for k in islice(it, SIZE)}

    def run(self):
        mysql_con = Con(self.con_cfg).mysql_con()
        data = read_data(self.text_embedding_cfg['text_db_info'], mysql_con)
        mysql_con.close()
        item_ids = data[self.text_embedding_cfg['data_info']['item_id_col']]
        texts = data[self.text_embedding_cfg['data_info']['text_col']]
        texts_embedding = self.gen_embedding(texts)
        texts_embedding_dict = {k: v for k, v in zip(item_ids, texts_embedding)}
        for sub_texts_embedding in self.chunks(texts_embedding_dict):
            response = self.write_to_engine(sub_texts_embedding, self.text_embedding_cfg['milvus_db_info'])
            print(response)
