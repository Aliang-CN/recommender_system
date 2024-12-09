# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : etl_op.py
# Time       ：2023/8/7 15:57
# Author     ：aliang
"""

import pandas as pd


class OLAPOp(object):
    @staticmethod
    def cal_hot_item_from_sql(con, params):
        sql = params['sql']
        col = params['col']
        topk = params['topk']
        df = pd.read_sql(sql, con)
        hot_item_list = df[col].to_list()[:topk]
        return {"hot_item": hot_item_list}

    @staticmethod
    def col_hot_item_from_df(df: pd.DataFrame, params: dict):
        col = params['col']
        prefix = params['prefix']
        if 'topk' in params.keys():
            topk = params['topk']
        else:
            topk = len(df) + 1
        hot_item_list = df[col].value_counts().index.values.tolist()[:topk]
        return {prefix: hot_item_list}

    @staticmethod
    def col_hot_item_groupby_from_df(df: pd.DataFrame, params: dict):
        hot_item_dict = {}
        col = params['col']
        prefix = params['prefix']
        groupby = params['groupby']
        if 'topk' in params.keys():
            topk = params['topk']
        else:
            topk = len(df) + 1
        for index, row in df.groupby(by=[groupby]):
            hot_item_list = row[col].value_counts().index.values.tolist()[:topk]
            hot_item_dict[prefix + '_{}'.format(str(index))] = hot_item_list
        return hot_item_dict
