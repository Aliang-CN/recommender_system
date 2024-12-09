# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : streaming_engine.py
# Time       ：2023/8/17 17:29
# Author     ：aliang
"""

import time
from rocketmq.client import PushConsumer, ConsumeStatus, Producer, Message
import json
from rec.utils.common import read_config, gen_cfg_name, gen_global_cfg_name
from rec.utils.connection import Connection as Con
import nacos


class MQProuduct(object):
    def __init__(self):
        self.producer = Producer('PID_001', max_message_size=1024 * 1024)
        self.producer.set_name_server_address('localhost:9876')  # ip和端口
        self.producer.start()

    def write(self, msg_body):
        date = time.strftime("%Y-%m-%d", time.localtime())
        msg = Message('ymt_test')
        msg.set_keys(date)
        msg.set_tags('test')
        msg.set_body(msg_body)
        ret = self.producer.send_sync(msg)
        print(ret.status, ret.msg_id, ret.offset)

    def shutdown(self):
        self.producer.shutdown()


class MQConsumer(object):
    def __init__(self, nacos_config=None, customer_id=None):
        self.autoNacos = nacos.AutoNacos()
        self.rq_cfg = self.autoNacos.get_config(gen_global_cfg_name('rq', customer_id))
        self.con_cfg = self.autoNacos.get_config(gen_global_cfg_name('connection', customer_id))

        self.redis_con = Con(self.con_cfg).redis_con()
        self.cols = self.rq_cfg['cols']
        self.consumer = PushConsumer(self.rq_cfg['consumer'])
        self.consumer.set_name_server_address('{}:{}'.format(self.con_cfg['rocketmq']['host'],
                                                             self.con_cfg['rocketmq']['port']))

    # def callback(self, msg):
    #     data = msg.body
    #     data = bytes.decode(data)
    #     data = json.loads(data)
    #     data = data['data']
    #     data = json.loads(data)
    #     if data['behavior_type'] == '2':
    #         self.redis_con.lpush('k11_hist_' + data['user_id'], data['item_id'])            # 写入hist
    #         self.redis_con.ltrim('k11_hist_' + data['user_id'], -30, -1)
    #         print('k11_hist_' + data['user_id'], self.redis_con.lrange('k11_hist_' + data['user_id'], 0, -1))
    #     return ConsumeStatus.CONSUME_SUCCESS

    def callback(self, msg):
        """
        Examlpe
            #     data = msg.body
    #     data = bytes.decode(data)
    #     data = json.loads(data)
    #     data = data['data']
    #     data = json.loads(data)
    #     return ConsumeStatus.CONSUME_SUCCESS
        """
        pass

    def consume(self):
        print('consume')
        self.consumer.subscribe(self.rq_cfg['producer'], self.callback)
        self.consumer.start()

    def shutdown(self):
        self.consumer.shutdown()


if __name__ == '__main__':
    mqc = MQConsumer()
    mqc.consume()
    while True:
        time.sleep(30)
