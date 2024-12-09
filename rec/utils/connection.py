# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : connection.py
# Time       ：2023/8/10 14:14
# Author     ：aliang
"""
import boto3
from botocore.client import Config
# from pyhive import hive
import pymysql
import happybase
from clickhouse_driver import Client
from realtime_rec.utils.common import read_config
import redis
import nacos
from elasticsearch import Elasticsearch
from ceph_api.ceph_base.ceph_boto3_s3_api import CephBoto3S3Api


class Connection(object):
    def __init__(self, config=None):
        if isinstance(config, str):
            self.config = read_config(config)
        elif isinstance(config, dict):
            self.config = config
        else:
            self.autoNacos = nacos.AutoNacos()
            self.config = self.autoNacos.get_config("connection")

    # def hive_con(self, database=None):
    #     if database == None:
    #         database = self.config['hive']['database']
    #     con = hive.Connection(host=self.config['hive']['host'],
    #                           port=self.config['hive']['port'],
    #                           username=self.config['hive']['username'],
    #                           database=database)
    #     return con

    def hbase_con(self):
        con = happybase.Connection(host=self.config["hbase"]["host"],
                                   port=self.config['hbase']['port'])
        return con

    def mysql_con(self, database=None):
        if database == None:
            database = self.config['mysql']['database']
        con = pymysql.connect(host=self.config['mysql']['host'],
                              port=self.config['mysql']['port'],
                              user=self.config['mysql']['username'],
                              password=self.config['mysql']['password'],
                              db=database,
                              charset='utf8mb4')
        return con

    def clickhouse_con(self, database=None, send_receive_timeout=5):
        if database == None:
            database = self.config['clickhouse']['database']
        con = Client(host=self.config['clickhouse']['host'],
                     port=self.config['clickhouse']['port'],
                     user=self.config['clickhouse']['user'],
                     database=database,
                     send_receive_timeout=send_receive_timeout)
        return con

    def redis_con(self, db=None):
        pool = redis.ConnectionPool(host=self.config['redis']["host"],
                                    port=self.config['redis']["port"],
                                    password=self.config['redis']['password'],
                                    decode_responses=True, max_connections=100)
        con = redis.Redis(connection_pool=pool)
        return con

    def es_con(self, ):
        es_con = Elasticsearch([{'host': self.config['es']['host'],
                                 'port': self.config['es']['port']}])
        return es_con


class CephClient(CephBoto3S3Api):
    def __init__(self, config=None):
        if isinstance(config, str):
            self.config = read_config(config)
        elif isinstance(config, dict):
            self.config = config
        else:
            self.autoNacos = nacos.AutoNacos()
            self.config = self.autoNacos.get_config("connection")
        self.access_key = self.config['ceph']['access_key']
        self.secret_key = self.config['ceph']['secret_key']
        self.url = self.config['ceph']['endpoint_url']
        self.s3 = boto3.client('s3', aws_access_key_id=self.access_key,
                               aws_secret_access_key=self.secret_key,
                               endpoint_url=self.url,
                               config=Config(signature_version='s3v4'))
        CephBoto3S3Api.__init__(self, self.access_key, self.secret_key, self.url)
        self._io_threads = 2

    def get_file_info(self, bucket_name, key_name):
        """
        :desc 获取文件信息
        :param bucket_name:
        :param key_name:
        :return:
        """
        file_info = {}
        if self.bucket_exist(bucket_name=bucket_name):
            contents = self.bucket_all_contents(bucket_name)
            for content in contents:
                if content["Key"] == key_name:
                    file_info = content
                    break
        return file_info

    def file_exist(self, bucket_name, key_name):
        """
        :desc 判断文件在bucket中是否存在
        :param bucket_name:
        :return: 存在返回True，否则返回False
        """
        files_list = self.get_files_list(bucket_name=bucket_name)
        return key_name in files_list

    def generate_presigned_url(self, bucket_name, key_name):
        return self.s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': bucket_name,
                                                                                 'Key': key_name},
                                              ExpiresIn=604800)
