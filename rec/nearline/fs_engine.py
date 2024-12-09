# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : fs_engine.py
# Time       ：2023/10/11 14:28
# Author     ：aliang
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import TableEnvironment,EnvironmentSettings
import pandas as pd
import sys
sys.path.append('../../')
from feature_flow.utils.flow_util import parse_schema, checkpath, read_config_file
from feature_flow.op.flink_op.udaf import KeyWindow, HistTop10
from feature_flow.op.flink_op.udf import Plus2, StringIndexer, CatCross


class OfflineFlow:
    def __init__(self,file_path=None, sink_name='print'):
        self.configs = read_config_file(file_path)
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.t_env = TableEnvironment.create(environment_settings=EnvironmentSettings.new_instance().in_batch_mode().use_blink_planner().build())
        self.env = StreamExecutionEnvironment.get_execution_environment()
        # self.t_env.get_config().get_configuration().set_string("pipeline.jars", 'file:///home/hadoop/flink-1.13.2/lib/flink-sql-parquet_2.11-1.13.0.jar')
        self.t_env.get_config().get_configuration().set_string("pipeline.jars", 'file:///home/hadoop/flink-1.13.2/lib/rocketmq-flink-1.0.0-SNAPSHOT.jar')

        self.schemas = self.configs['schemas']
        self.head = self.configs['head']
        self.source_data_path = self.configs['source_data_path']
        self.result_data_path = self.configs['result_data_path']
        self.operators = self.configs['operators']
        self.is_index = False
        for operator in self.operators:
            if operator['hp_subspace'] == "StringIndexer":
                self.is_index = True
        self.sink_name = sink_name
        self._init_table()

    def _init_table(self):
        self.create_source_table()
        self.table = self.t_env.from_path("adult")

    def _init_pipeline(self, table, table_name="my_table"):
        self.t_env.create_temporary_view(table_name, table)

        sql_ddl = f"""SELECT *,"""
        for operator in self.operators:
            op_func = eval(operator['hp_subspace'])(operator)
            self.t_env.create_temporary_function(op_func.name, op_func.func)
            sql_ddl, self.head = op_func.offline_ddl(sql_ddl, self.head, self.is_index)

        sql_ddl = sql_ddl[:-1] + f" from {table_name}"
        print(sql_ddl)
        table = self.t_env.sql_query(sql_ddl)

        return table

    def get_online_feature_service(self):
        results = self._init_pipeline(self.table)
        sink_name = self.create_sink_table(results)
        results.execute_insert(sink_name).wait()

    def get_offline_features(self):
        results = self._init_pipeline(self.table)
        sink_name = self.create_sink_table(results, sink_name=self.sink_name)
        results.execute_insert(sink_name).wait()

    def create_source_table(self, source_way="sql"):
        source_name = "adult"
        if source_way == "table":
            pdf = pd.read_csv(self.source_data_path, names=self.head)
            table = self.t_env.from_pandas(pdf)
            self.t_env.create_temporary_view(source_name, table)
        else:
            self.t_env.execute_sql(
                f"""
                    create table {source_name}(
                        {self.schemas}
                    ) with (
                        'connector' = 'rocketmq',
                        'topic' = 'k11_online_behaviors_mysql_topic',
                        'nameServerAddress' = '192.168.50.152:9876'
                    )
                    """)
        return source_name

    def create_sink_table(self, table, sink_name="print"):
        out_schema = parse_schema(table.get_schema())
        checkpath(self.result_data_path+"/"+sink_name)
        if sink_name != "print":
            self.t_env.execute_sql(f"""
                           CREATE TABLE `{sink_name}`(
                                {out_schema}
                            ) WITH (
                                    'connector' = 'filesystem',
                                    'path' = '{self.result_data_path}/{sink_name}',
                                    'format' = 'csv'
                                    )
                                """)
        else:
            self.t_env.execute_sql(f"""
                CREATE TABLE {sink_name}(
                    {out_schema}
                ) WITH (
                    'connector' = 'print'
                )
            """)
        return sink_name