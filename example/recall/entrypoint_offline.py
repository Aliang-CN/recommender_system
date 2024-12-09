# !/usr/bin/env python
# -*-coding:utf-8 -*-
import copy
import grpc
import logging
import traceback
import uuid
from google.protobuf.json_format import MessageToJson
import google.protobuf.text_format as text_formats

from typing import List
from pydantic import BaseModel

logging.basicConfig(filename='./log/offline_entrypoint.log',format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', level = logging.INFO,filemode='a',datefmt='%Y-%m-%d%I:%M:%S %p')


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


RECALL_HOST = 'service-autorecall-recall'
RECALL_PORT = '8080'
recall_channel = grpc.insecure_channel("{}:{}".format(RECALL_HOST, RECALL_PORT))


def recall(req:RequestBody, param):
    from AutoRecall.proto import recall_pb2, recall_pb2_grpc
    client = recall_pb2_grpc.RecallServiceStub(channel=recall_channel)
    request_info = recall_pb2.RecallRequest()
    request_info.Param = param #json param
    request_info.ReqBase.BzName = "k11"
    request_info.ReqBase.BzId = 1
    request_info.ReqBase.SceneId = 1
    request_info.ReqBase.SceneName = "offline"
    req.c_mode = "offline"
    request_info.ReqBase.RecNum = 50
    request_info.ReqBase.UserInfo.UserId = req.c_user_id
    request_info.ReqBase.HasSupplement = req.additional.is_padding
    request_info.ReqBase.TraceId = uuid.uuid1().hex

    ctx_info = request_info.ReqBase.CtxInfo
    if req.additional.m_groups != "":
        filter_infos = ctx_info.FilterInfos.add()
        filter_infos.Field = "m_groups"
        group_array = req.additional.m_groups.split(",")
        for i in range(len(group_array)):
            filter_infos.Vals.append(group_array[i])

    if req.additional.store_code is not None and len(req.additional.store_code) > 0:
        filter_infos = ctx_info.FilterInfos.add()
        filter_infos.Field = "store_code"
        for i in range(len(req.additional.store_code)):
            filter_infos.Vals.append(req.additional.store_code[i])

    if req.additional.brand_code is not None and len(req.additional.brand_code) > 0:
        filter_infos = ctx_info.FilterInfos.add()
        filter_infos.Field = "brand_code"
        for i in range(len(req.additional.brand_code)):
            filter_infos.Vals.append(req.additional.brand_code[i])

    if req.additional.goods_sn is not None and len(req.additional.goods_sn) > 0:
        filter_infos = ctx_info.FilterInfos.add()
        filter_infos.Field = "goods_sn"
        for i in range(len(req.additional.goods_sn)):
            filter_infos.Vals.append(req.additional.goods_sn[i])

    if req.additional.sb1_code is not None and len(req.additional.sb1_code) > 0:
        filter_infos = ctx_info.FilterInfos.add()
        filter_infos.Field = "sb1_code"
        for i in range(len(req.additional.sb1_code)):
            filter_infos.Vals.append(str(req.additional.sb1_code[i]))

    if req.additional.sb2_code is not None and len(req.additional.sb2_code) > 0:
        filter_infos = ctx_info.FilterInfos.add()
        filter_infos.Field = "sb2_code"
        for i in range(len(req.additional.sb2_code)):
            filter_infos.Vals.append(str(req.additional.sb2_code[i]))

    if req.additional.floor is not None and len(req.additional.floor) > 0:
        filter_infos = ctx_info.FilterInfos.add()
        filter_infos.Field = "floor"
        for i in range(len(req.additional.floor)):
            filter_infos.Vals.append(req.additional.floor[i])

    if req.additional.unitcode is not None and len(req.additional.unitcode) > 0:
        filter_infos = ctx_info.FilterInfos.add()
        filter_infos.Field = "unitcode"
        for i in range(len(req.additional.unitcode)):
            filter_infos.Vals.append(req.additional.unitcode[i])

    if req.additional.mall_code is not None and len(req.additional.mall_code) > 0:
        filter_infos = ctx_info.FilterInfos.add()
        filter_infos.Field = "mall_code"
        for i in range(len(req.additional.mall_code)):
            filter_infos.Vals.append(req.additional.mall_code[i])

    default_reg = ["WH","SY","TJ","GZ","SH"]
    diff_set = set([])
    has_partition_tags = False
    if len(req.partition_tags) > 0:
        for i in range(len(req.partition_tags)):
            if req.partition_tags[i] == "_default":
                for i, val in enumerate(default_reg):
                    diff_set.add(val)
                break
            else:
                diff_set.add(req.partition_tags[i])
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

RERANK_HOST = 'service-autorecall-rerank'
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
        logging.info("rerank response:%s",text_formats.MessageToString(response))
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
        sub_data['rank'] = i 
        sub_data['c_off_item_id'] =  response.MixItem.Items[i].ItemId
        rsp['data'].append(sub_data)
        cnt += 1
        if cnt >= rec_num:
            break
    return rsp

from dask.threaded import get
from fastapi import FastAPI,Request,Body 
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error("parameter invaild, request body:%s", request.body())
    return JSONResponse({"code":400, "message":"parameter invaild", "data":None})

@app.post("/k11/rec_list")
async def root(requestBody: RequestBody):
    dag = {
        'recall': (recall, requestBody,'{"Label":"nearline","ResourceInfos":[{"Type":"milvus", "Table":"k11_online_vector", "Topk":200, "RelevantTable":"k11_offline_vector"}], "UserPrefix":{"UserBehaviorPrefixs":[{"BehaviorKeyPrefix":"k11_hist_", "Topk":30}],"UserMapping":{"UserMappingPrefix":"k11_user_mapping_", "MemberKey":"member_id"}}}'),
        'rerank': (rerank, 'recall','{"Lable":"k11","FilterResInfo":{"Type":"elasticsearch", "Table":"k11_offline_goods"}, "SupplementResInfos":[{"Type":"redis", "Table":"k11_hot_item_offline", "Topk":100}], "Flowinfo":{"Callers":["filter", "supplement"]}}'),
    }
    return get(dag, 'rerank')


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
