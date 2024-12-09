# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : curd.py
# Time       ：2023/8/19 17:52
# Author     ：aliang
"""
import pandas as pd
from rec.utils.connection import Connection as Con


def write_df_to_mysql(con, df, table_name):
    df = df.dropna(axis=0, how='any')
    cursor = con.cursor()
    keys = df.keys()
    values = df.values.tolist()
    key_sql = ','.join(keys)
    value_sql = ','.join(['%s'] * df.shape[1])
    insert_data_str = """REPLACE INTO %s (%s) values (%s)""" % (table_name, key_sql, value_sql)
    cursor.executemany(insert_data_str, values)
    con.commit()
    cursor.close()
    con.close()


if __name__ == '__main__':
    df = pd.read_csv('../../data/train_data/deepfm/item.csv')
    mysql_con = Con('../config/connection.yaml').mysql_con(database='ymt')
    write_df_to_mysql(mysql_con, df, table_name='item')