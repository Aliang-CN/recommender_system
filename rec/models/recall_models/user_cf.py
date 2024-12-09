# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : usercf.py
# Time       ：2023/8/23 11:47
# Author     ：aliang
"""
from tqdm import tqdm
from collections import defaultdict
import math


class UserCF(object):
    def __init__(self):
        pass

    def get_sim_user(self, df):
        # user_min_time_dict = get_user_min_time_dict(df, user_col, item_col, time_col) # user first time
        # history
        user_item_time_dict = self.get_user_item_time_dict(df)  # {'user_id':[[item_id, time],[item_id2, time2]]}
        # item, [u1, u2, ...,]
        item_user_time_dict = self.get_item_user_time_dict(df)  #

        sim_user = {}
        user_cnt = defaultdict(int)
        for item, user_time_list in tqdm(item_user_time_dict.items()):
            num_users = len(user_time_list)
            for u, t in user_time_list:
                user_cnt[u] += 1
                sim_user.setdefault(u, {})
                for relate_user, relate_t in user_time_list:
                    # time_diff_relate_u = 1.0/(1.0+10000*abs(relate_t-t))
                    if u == relate_user:
                        continue
                    sim_user[u].setdefault(relate_user, 0)
                    weight = 1.0
                    sim_user[u][relate_user] += weight / math.log(1 + num_users)

        sim_user_corr = sim_user.copy()
        for u, related_users in tqdm(sim_user.items()):
            for v, cuv in related_users.items():
                sim_user_corr[u][v] = cuv / math.sqrt(user_cnt[u] * user_cnt[v])

        return sim_user_corr, user_item_time_dict

    def get_item_user_time_dict(self, df, user_col='c_user_id', item_col='c_item_id', time_col='t_time'):
        item_user_df = df.sort_values(by=[item_col, time_col])
        item_user_df = item_user_df.groupby(item_col).apply(
            lambda group: self.make_user_time_tuple(group, user_col, item_col, time_col)).reset_index().rename(
            columns={0: 'user_id_time_list'})
        item_user_time_dict = dict(zip(item_user_df[item_col], item_user_df['user_id_time_list']))
        return item_user_time_dict

    def get_user_item_time_dict(self, df, user_col='c_user_id', item_col='c_item_id', time_col='t_time',
                                is_drop_duplicated=False):
        user_item_ = df.sort_values(by=[user_col, time_col])  # 进行排序，按照用户，时间进行
        if is_drop_duplicated:
            print('drop_duplicates ..')
            user_item_ = user_item_.drop_duplicates(subset=['c_user_id', 'c_item_id'], keep='last')  # 去重

        user_item_ = user_item_.groupby(user_col).apply(
            lambda group: self.make_item_time_tuple(group, user_col, item_col, time_col)).reset_index().rename(
            columns={0: 'item_id_time_list'})  # 按照时间进行排序聚合

        user_item_time_dict = dict(zip(user_item_[user_col], user_item_['item_id_time_list']))
        return user_item_time_dict  # return: {'user_id':[[item_id, time],[item_id2, time2]]}  # 返回一个用户对应的item时间列表

    def make_item_time_tuple(self, group_df, user_col='c_user_id', item_col='c_item_id', time_col='t_time'):
        user_time_tuples = list(zip(group_df[item_col], group_df[time_col]))
        return user_time_tuples

    def make_user_time_tuple(self, group_df, user_col='c_user_id', item_col='c_item_id', time_col='t_time'):
        user_time_tuples = list(zip(group_df[user_col], group_df[time_col]))
        return user_time_tuples
