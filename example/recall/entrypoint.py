
# !/usr/bin/env python
# -*-coding:utf-8 -*-
import copy
import grpc
import json
import logging
import traceback
import uuid

from typing import List
from pydantic import BaseModel

logging.basicConfig(filename='./log/online_entrypoint.log',format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', level = logging.INFO,filemode='a',datefmt='%Y-%m-%d%I:%M:%S %p')

class Additional(BaseModel):
    mall_code: List[str]=None
    store_code: List[str]=None
    goods_sn: List[str]=None
    brand_code: List[str]=None
    sb1_code: List[int]=None
    sb2_code: List[int]=None
    floor: List[str]=None
    unitcode: List[str]=None
    m_groups: str=""
    is_padding: int=0
    is_test: str="0"


class RequestBody(BaseModel):
    c_session_id: str
    token: str
    c_user_id: str
    c_mode: str
    partition_tags: List[str]
    additional: Additional


class RequestInfo:
    def __init__(self):
        pass

    def __init__(self, Param, ReqBase, MixItems, Items, response):
        self.ReqBase = ReqBase
        self.Param = Param
        self.MixItems = MixItems
        self.Items = Items
        self.response = response


RECALL_HOST = 'autorecall-recall-service'
RECALL_PORT = '8080'
recall_channel = grpc.insecure_channel("{}:{}".format(RECALL_HOST, RECALL_PORT))

def recall(query_json, param):
    from AutoRecall.proto import recall_pb2, recall_pb2_grpc
    client = recall_pb2_grpc.RecallServiceStub(channel=recall_channel)
    request_info = recall_pb2.RecallRequest()
    request_info.Param = param #json param
    request_info.ReqBase.BzName = "k11"
    request_info.ReqBase.BzId = 1
    request_info.ReqBase.SceneId = 1
  
    if "c_mode" in query_json:
        c_mode = query_json['c_mode']
        if c_mode != "online":
            c_mode = "offline"
    else:
        c_mode = "offline"
    request_info.ReqBase.SceneName = c_mode
    request_info.ReqBase.RecNum = 50
    request_info.ReqBase.UserInfo.UserId = query_json['c_user_id']
    is_padding = 0
    request_info.ReqBase.TraceId = uuid.uuid1().hex

    if "additional" in query_json:
        if "is_padding" in query_json["additional"]:
            is_padding = query_json["additional"]["is_padding"]
        request_info.ReqBase.HasSupplement = is_padding

        is_test="0"
        if "is_test" in query_json["additional"]:
            is_test = query_json["additional"]["is_test"]

        if is_test != "0":
            request_info.ReqBase.DebugMode = True
    
        ctx_info = request_info.ReqBase.CtxInfo
        if "m_groups" in query_json["additional"]:
            m_groups = query_json["additional"]["m_groups"]
            if m_groups != "":
                filter_infos = ctx_info.FilterInfos.add()
                filter_infos.Field = "m_groups"
                group_array = m_groups.split(",")
                for i in range(len(group_array)):
                    filter_infos.Vals.append(group_array[i])

        if "store_code" in query_json["additional"]:
            store_code_array = query_json["additional"]["store_code"]
            if len(store_code_array) > 0:
                filter_infos = ctx_info.FilterInfos.add()
                filter_infos.Field = "store_code"
                for i in range(len(store_code_array)):
                    filter_infos.Vals.append(store_code_array[i])

        if "brand_code" in query_json["additional"]:
            brand_code_array = query_json["additional"]["brand_code"]
            if len(brand_code_array) > 0:
                filter_infos = ctx_info.FilterInfos.add()
                filter_infos.Field = "brand_code"
                for i in range(len(brand_code_array)):
                    filter_infos.Vals.append(brand_code_array[i])

        if "goods_sn" in query_json["additional"]:
            goods_sn_array = query_json["additional"]["goods_sn"]
            if len(goods_sn_array) > 0:
                filter_infos = ctx_info.FilterInfos.add()
                filter_infos.Field = "goods_sn"
                for i in range(len(goods_sn_array)):
                    filter_infos.Vals.append(goods_sn_array[i])

        if "sb1_code" in query_json["additional"]:
            sb1_code_array = query_json["additional"]["sb1_code"]
            if len(sb1_code_array) > 0:
                filter_infos = ctx_info.FilterInfos.add()
                filter_infos.Field = "sb1_code"
                for i in range(len(sb1_code_array)):
                    filter_infos.Vals.append(sb1_code_array[i])

        if "sb2_code" in query_json["additional"]:
            sb2_code_array = query_json["additional"]["sb2_code"]
            if len(sb2_code_array) > 0:
                filter_infos = ctx_info.FilterInfos.add()
                filter_infos.Field = "sb2_code"
                for i in range(len(sb2_code_array)):
                    filter_infos.Vals.append(sb2_code_array[i])
            
        if "floor" in query_json["additional"]:
            floor_array = query_json["additional"]["floor"]
            if len(floor_array) > 0:
                filter_infos = ctx_info.FilterInfos.add()
                filter_infos.Field = "floor"
                for i in range(len(floor_array)):
                    filter_infos.Vals.append(floor_array[i])

        if "unitcode" in query_json["additional"]:
            unitcode_array = query_json["additional"]["unitcode"]
            if len(unitcode_array) > 0:
                filter_infos = ctx_info.FilterInfos.add()
                filter_infos.Field = "unitcode"
                for i in range(len(unitcode_array)):
                    filter_infos.Vals.append(unitcode_array[i])

        if "mall_code" in query_json["additional"]:
            mall_code_array = query_json["additional"]["mall_code"]
            if len(unitcode_array) > 0:
                filter_infos = ctx_info.FilterInfos.add()
                filter_infos.Field = "mall_code"
                for i in range(len(mall_code_array)):
                    filter_infos.Vals.append(mall_code_array[i])

    default_reg = ["WH","SY","TJ","GZ","SH"]
    diff_set = set([])
    has_partition_tags = False
    if "partition_tags" in query_json:
        partition_tags_array = query_json["partition_tags"]
        for i in range(len(partition_tags_array)):
            if partition_tags_array[i] == "_default":
                for i, val in enumerate(default_reg):
                    diff_set.add(val)
                break
            else:
                diff_set.add(partition_tags_array[i])
            has_partition_tags = True
        
    if has_partition_tags is True:
        filter_infos = ctx_info.FilterInfos.add()
        filter_infos.Field = "mall_code"
        filter_infos.Type = 10 #prefix match
        for v in iter(diff_set):
            filter_infos.Vals.append(v)

    try:  
        response = client.DoRecall(request_info, timeout=0.5)
        return response
    except Exception as e:
        rsp = recall_pb2.RecallResponse()
        rsp.ReqBase.CopyFrom(request_info.ReqBase)
        logging.error(traceback.format_exc())
        return rsp

MERGE_HOST = 'autorecall-merge-service'
MERGE_PORT = '8080'
merge_channel = grpc.insecure_channel("{}:{}".format(MERGE_HOST, MERGE_PORT))


def merge(req, param):
    from AutoRecall.proto import merge_pb2, merge_pb2_grpc, common_pb2
    client = merge_pb2_grpc.MergeServiceStub(channel=merge_channel)
    request_info = merge_pb2.MergeRequest()
    request_info.Param = param #req.Param

    for i in range(len(req)):
        request_info.MixItems.append(req[i].MixItem)

    request_info.ReqBase.CopyFrom(req[0].ReqBase)
    try:
        response = client.DoMerge(request_info, timeout=0.2)
        return response
    except Exception as e:
        rsp = merge_pb2.MergeResponse()
        rsp.ReqBase.CopyFrom(request_info.ReqBase)
        logging.error(traceback.format_exc())
        return rsp
    
RANK_HOST = 'autorecall-rank-service'
RANK_PORT = '8080'
rank_channel = grpc.insecure_channel("{}:{}".format(RANK_HOST, RANK_PORT))

def rank(req, param):
    from AutoRecall.proto import rank_pb2, rank_pb2_grpc
    client = rank_pb2_grpc.RankServiceStub(channel=rank_channel)
    request_info = rank_pb2.RankRequest()
    request_info.Param = param 
    request_info.MixItem.CopyFrom(req.MixItem)
    request_info.ReqBase.CopyFrom(req.ReqBase)
    try:
        response = client.DoRank(request_info, timeout=0.5)
        return response
    except Exception as e:
        rsp = rank_pb2.RankResponse()
        rsp.ReqBase.CopyFrom(request_info.ReqBase)
        rsp.MixItem.CopyFrom(req.MixItem)
        logging.error(traceback.format_exc())
        return rsp

RERANK_HOST = 'autorecall-rerank-service'
RERANK_PORT = '8080'
rerank_channel = grpc.insecure_channel("{}:{}".format(RERANK_HOST, RERANK_PORT))

def rerank(req, param):
    from AutoRecall.proto import rerank_pb2, rerank_pb2_grpc
    client = rerank_pb2_grpc.RerankServiceStub(channel=rerank_channel)
    request_info = rerank_pb2.RerankRequest()
    request_info.Param = param
    request_info.MixItem.CopyFrom(req.MixItem)
    request_info.ReqBase.CopyFrom(req.ReqBase)
    try:
        response = client.DoRerank(request_info, timeout=3)
        return buildhttpresponse(response)
    except Exception as e:
        rsp = rerank_pb2.RerankResponse()
        rsp.ReqBase.CopyFrom(request_info.ReqBase)
        rsp.MixItem.CopyFrom(req.MixItem)
        logging.error(traceback.format_exc())
        return buildhttpresponse(rsp)

def buildhttpresponse(response):
    rsp = dict()
    rsp['code'] = 0
    rsp['message'] = 'reclist'
    rsp['trace_id'] = response.ReqBase.TraceId
    rsp['data'] = list()
    rec_num = response.ReqBase.RecNum
    cnt = 0
    logging.info("real recommend items total:%d", len(response.MixItem.Items))
    for i in range(len(response.MixItem.Items)):
        sub_data = dict()
        cnt += 1
        if response.ReqBase.SceneName == "online":
            sub_data['c_on_item_id'] =  response.MixItem.Items[i].ItemId
            sub_data['rank'] = float(i+1) 
        else:
            sub_data['c_off_item_id'] =  response.MixItem.Items[i].ItemId
            sub_data['rank'] = i+1 
        rsp['data'].append(sub_data)
        if cnt >= rec_num:
            break
    return text(json.dumps(rsp))

from dask.threaded import get
from sanic import Sanic
import json
from sanic.response import text
app = Sanic("k11 rec_list")

async def server_error_handler(request, exception):
    rsp = dict()
    rsp['code'] = 5001
    rsp['message'] = 'Oops, server error'
    rsp['data'] = list()
    logging.info("exception: {}".format(exception))
    return text(json.dumps(rsp))

app.error_handler.add(Exception, server_error_handler)

@app.route('/k11/rec_list', methods=['POST'])
async def k11_rec_list(request):
    try:
        query_json = request.json
        logging.info("query Body:%s", query_json)
        if "token" not in query_json or query_json['token']!="azEx5o6o6I2Q5pyN5Yqh":
            rsp = dict()
            rsp['code'] = 4001
            rsp['message'] = 'param invaild, token error'
            rsp['data'] = list()
            return text(json.dumps(rsp))
        
        if "c_mode" in query_json:
            c_mode = query_json['c_mode']
            if c_mode != "online":
                c_mode = "offline"
        else:
            c_mode = "offline"
        print(c_mode)
        logging.info("c_mode:%s", c_mode)

        if c_mode == "online":
            dag = {
                'recall': (recall, query_json,'{"Label":"nearline","ResourceInfos":[{"Type":"milvus", "Table":"k11_deepwalk_online", "Topk":400}],"UserPrefix":{"UserBehaviorPrefixs":[{"BehaviorKeyPrefix":"k11_hist_", "Topk":30}], "UserMapping":{"UserMappingPrefix":"k11_user_mapping_", "MemberKey":"member_id"}}}'),
                'rank': (rank, 'recall', '{"Feature":{"user_feature":{"cate_cols":["member_id","level_id","is_special_level","city","province","country","sex","reg_origin","reg_sub_origin","up_origin","operator_type","kpoint"]},"item_feature":{"num_cols":["min_price","max_price"],"cate_cols":["goods_sn","area_id","guide_weight","guide_color","mer_id","store_code","type","cash_type","member_cash_type","card_type","cate_id","effect_type","buy_limit_type","is_shipping","shipping_express","shipping_store","return_time","services","is_on_sale","whole_is_on_sale","is_recommend","purchase","spec_num","sales","pviews","tag_kp_cash","tag_kp_multiple","is_cart","is_special", "m_groups"]}}, "UserPrefix":{"UserPrefix":"k11_user_", "ItemPrefix":"k11_online_goods_"}}'),
                'rerank': (rerank, 'rank','{"Lable":"k11","FilterResInfo":{"Type":"elasticsearch","Table":"k11_online_goods"}, "SupplementResInfos":[{"Type":"redis", "Table":"k11_hot_item_online", "Topk":100}],"Flowinfo":{"Callers":["filter", "supplement"]}}'),
            }
            return get(dag, 'rerank')
        elif c_mode == "offline" or c_mode == "":
            dag = {
                'recall': (recall, query_json,'{"Label":"nearline","ResourceInfos":[{"Type":"milvus", "Table":"k11_online_vector", "Topk":400, "RelevantTable":"k11_offline_vector"}], "UserPrefix":{"UserBehaviorPrefixs":[{"BehaviorKeyPrefix":"k11_hist_", "Topk":30}],"UserMapping":{"UserMappingPrefix":"k11_user_mapping_", "MemberKey":"member_id"}}}'),
                'rerank': (rerank, 'recall','{"Lable":"k11","FilterResInfo":{"Type":"elasticsearch", "Table":"k11_offline_goods"}, "SupplementResInfos":[{"Type":"redis", "Table":"k11_hot_item_offline", "Topk":100}], "Flowinfo":{"Callers":["filter", "supplement"]}}'),
            }
            return get(dag, 'rerank')
        else:
            rsp = dict()
            rsp['code'] = 4001
            rsp['message'] = 'param invaild'
            rsp['data'] = list()
            logging.info("param invaild error,req:%s", query_json)
            return text(json.dumps(rsp))
    except Exception as e:
        logging.error(traceback.format_exc())
        rsp = dict()
        rsp['code'] = 5001
        rsp['message'] = 'internal error'
        rsp['data'] = list()
        logging.info("internal error,req:%s", request.json)
        return text(json.dumps(rsp))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, workers=1, debug=False)
