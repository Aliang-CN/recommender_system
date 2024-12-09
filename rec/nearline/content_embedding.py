import nacos
import grpc
import pandas as pd
from rec.utils.common import read_data, read_config
from sentence_transformers import SentenceTransformer
from rec.protobuf import vector_engine_pb2, vector_engine_pb2_grpc
from itertools import islice
from rec.utils.connection import Connection as Con
import urllib


class CVEmbeddingEngine(object):
    def __init__(self, config=None):
        self.autoNacos = nacos.AutoNacos(nacos_file=config)
        self.text_embedding_cfg = self.autoNacos.get_config('text_embedding')
        self.con_cfg = self.autoNacos.get_config('connection')
        self.model = self.load_model()

    def load_model(self):
        pass

    def gen_embedding(self, pic):
        embeddings = self.model.pridict(pic)
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
        mysql_con = Con().mysql_con()
        data = read_data(self.text_embedding_cfg['text_db_info'], mysql_con)
        mysql_con.close()
        item_ids = data[self.text_embedding_cfg['data_info']['item_id_col']]
        pic_url = data[self.text_embedding_cfg['data_info']['url_col']]
        pic = urllib.urlretrieve(pic_url, full_path)
        cv_embedding = self.gen_embedding(pic)
        texts_embedding_dict = {k: v for k, v in zip(item_ids, texts_embedding)}
        for sub_texts_embedding in self.chunks(texts_embedding_dict):
            response = self.write_to_engine(sub_texts_embedding, self.text_embedding_cfg['milvus_db_info'])
            print(response)
