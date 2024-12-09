# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : test_connection.py
# Time       ：2021/9/14 16:00
# Author     ：linxingliang
"""
import pandas as pd

from realtime_rec.utils.connection import CephClient, Connection


if __name__ == '__main__':
    access_key = "1O8WJ1EC77JG6S0TI5TR"
    secret_key = "Xmm3vztjEbeABQsriFbGmCbyN9c8fugNd6rxXHX9"
    endpoint_url = "http://192.168.50.23:7480"
    ceph = CephClient()
    remote_path = 'k11/save_model/deepfm/enc_data'
    resp = ceph.get_files_list(bucket_name='k11')
    # resp = ceph._conn_s3.get_object(Bucket="deep-runtime", Key="test_data/online_goods.csv")
    # s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key, endpoint_url=endpoint_url,
    #                   config=Config(signature_version='s3v4'))
    # url1 = s3.generate_presigned_url(
    #     ClientMethod='get_object',
    #     Params={
    #         'Bucket': 'deep-runtime',
    #         'Key': 'test_data/online_goods.csv'
    #     },
    #     ExpiresIn=604800
    # )
    url = ceph.generate_presigned_url(bucket_name='deep-runtime', key_name='test_data/online_goods.csv')
    data = pd.read_csv(url)
    print(data)
    # bucket = 'k11'
    # path = 'save_model/deepfm/enc_data.pkl'
    # save_file_name = '../../cache/enc_data'
    # resp = ceph.download_file(save_file_name, bucket, path, always_overwrite=True)
    # print(resp)

    # con = Connection()
    # es_con = con.es_con()
    # es_con.index(index="test", id='1',
    #          body={"first_name": "xiao", "last_name": "ming", 'age': 29, 'about': 'I love to go rock climbing',
    #                'interests': ['game', 'play']})
    # print('done')

    # query = {
    #     "query": {
    #         "match": {
    #             "first_name": "xiao"
    #         }
    #     }
    # }

    # result = es_con.search(index="test", body=query)
    # print(result)