# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : es_op.py
# Time       ：2021/9/1 14:38
# Author     ：aliang
"""
import jieba


class ESOp(object):
    """
    es 算子
    """
    @staticmethod
    def segment(data_list: list, params):
        """
        分词
        """
        for data in data_list:
            for col in params:
                data[col] = list(jieba.cut(data[col]))
        return data_list

    @staticmethod
    def split(data_list: list, params):
        """
        分割
        """
        for data in data_list:
            for col in params:
                data[col] = data[col].splist(',')
        return data_list
