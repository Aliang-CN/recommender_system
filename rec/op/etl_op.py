# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : etl.py
# Time       ：2023/8/2 19:07
# Author     ：aliang
"""

import pandas as pd
import random


class ETLOp(object):
    """
    etl 算子
    """
    @staticmethod
    def row_filter(df, params):
        """
        行过滤
        """
        if params['condition'] == '==':
            df = df[df[params['col']] == params['value']]
        elif params['condition'] == '>':
            df = df[df[params['col']] > params['value']]
        elif params['condition'] == '<':
            df = df[df[params['col']] < params['value']]
        else:
            raise Exception('err candition')
        return df

    @staticmethod
    def del_col(df, params):
        """
        删除某些列
            op: del_col
            params:
                cols: c_item_id, c_user_id                           # 要删掉的列
        """
        df = df.drop(columns=params['cols'])
        return df

    @staticmethod
    def drop_duplicates(df, params):
        cols = params['cols']
        """
        行去重
            op: drop_duplicates
            params:
                cols:
                  - c_item_id
        """
        df = df.drop_duplicates(cols, keep="last")
        return df

    @staticmethod
    def rename(df, params):
        """
        重命名
            op: rename
            params:
              cols:
                - user_profile_for_third_party.yid
                - user_profile_for_third_party.gender
                - user_profile_for_third_party.age
                - user_profile_for_third_party.user_level
                - user_profile_for_third_party.maincate
              new_cols:
                - c_user_id
                - c_gender
                - c_age
                - c_level
                - c_maincate
        """
        cols = params['cols']
        new_cols = params['new_cols']
        columns = {k: v for k, v in zip(cols, new_cols)}
        df.rename(columns=columns, inplace=True)
        return df

    @staticmethod
    def merge(behavior_df, user_df, item_df, params):
        """
        dataframe 合并
            op: rename
            params:
              col: c_item_id
        """
        user_col_name = params['user_col_name']
        item_col_name = params['item_col_name']
        behavior_df = behavior_df.merge(user_df, left_on=user_col_name, right_on=user_col_name)
        behavior_df = behavior_df.merge(item_df, left_on=item_col_name, right_on=item_col_name)
        return behavior_df

    @staticmethod
    def sort_get_head(df, params):
        """
        排序取头部
        op: sort_get_head
        params:
            topk: 100
            cols:
                - n_price
            ascending:
                - -1
        """
        cols = params['cols']
        ascending = params['ascending']
        topk = params['topk']
        df = df.sort_values(by=cols, ascending=ascending)
        df = df.groupby(by=cols).head(topk)
        return df

    @staticmethod
    def sort_values(df, params):
        """
        排序
        """
        cols = params['cols']
        ascending = params['ascending']
        df = df.sort_values(by=cols, ascending=ascending)
        return df

    @staticmethod
    def col_filter(df, params):
        """
        列过滤
        """
        cols = params['cols']
        df = df[cols]
        return df

    @staticmethod
    def normalization(df, params):
        """
        归一化，指定大小
        """
        for p in params:
            col = p['col']
            max = p['max']
            min = p['min']

            def _normalization(row, max, min):
                if row > max:
                    return 1
                elif row < min:
                    return 0
                else:
                    return (row - min) / (max - min)
            df[col] = df.apply(lambda x: _normalization(x[col], max, min), axis=1)
        return df

    @staticmethod
    def random_negative_sampling(df, params):
        """
        负采样
        op: random_negative_sampling
            params:
                ratio: 10                           # 采样比例
                user_id: c_user_id                  # 指定用户id列名
                item_id: c_item_id                  # 指定物品id列名
                behavior_type: c_behavior_type      # 指定行为id列名
                pos_value: click                    # 正样本值
                neg_value: view                     # 负样本值
                session_id: c_session_id            # session_id列名， 可选
        """

        ratio = params['ratio']
        user_id = params['user_id']
        item_id = params['item_id']
        behavior_type = params['behavior_type']
        pos_value = params['pos_value']
        if "|" in pos_value:
            pos_value = '|'.split(pos_value)
        else:
            pos_value = [pos_value]
        neg_value = params['neg_value']
        if "|" in neg_value:
            neg_value = "|".split(neg_value)
        else:
            neg_value = [neg_value]
        if 'session_id' in params.keys():
            session_id = params['session_id']
            by = [user_id, session_id]
        else:
            by = [user_id]

        users, items, label = [], [], []                        # 收集users, items, labels
        for group, row in df.groupby(by=by):
            if isinstance(group, tuple):
                group = group[0]
            if len(set(set(pos_value) & set(row[behavior_type].unique().tolist()))) >= 1:
            # if pos_value in row[behavior_type].unique().tolist():
                show_items = row[row[behavior_type].isin(pos_value)][item_id].to_list()
                for pos_i in row[row[behavior_type].isin(neg_value)][item_id].to_list():
                    users.append(group)
                    items.append(pos_i)
                    label.append(1)
                    if len(show_items) > ratio:
                        neg_i = random.choices(show_items, k=ratio)
                    else:
                        neg_i = show_items
                    users.extend([group] * len(neg_i))
                    items.extend(neg_i)
                    label.extend([0] * len(neg_i))
        df = {user_id: users, item_id: items, 'label': label}
        df = pd.DataFrame(df, columns=[user_id, item_id, 'label'])
        return df

    @staticmethod
    def global_random_negative_sampling(df, params):
        """
        负采样
        op: random_negative_sampling
            params:
                ratio: 10                           # 采样比例
                user_id: c_user_id                  # 指定用户id列名
                item_id: c_item_id                  # 指定物品id列名
                behavior_type: c_behavior_type      # 指定行为id列名
                pos_value: click                    # 正样本值
                neg_value: view                     # 负样本值
                session_id: c_session_id            # session_id列名， 可选
        """

        ratio = params['ratio']
        user_id = params['user_id']
        item_id = params['item_id']
        behavior_type = params['behavior_type']
        pos_value = params['pos_value']
        neg_value = params['neg_value']

        if "|" in pos_value:
            pos_value = '|'.split(pos_value)
        else:
            pos_value = [pos_value]
        if "|" in neg_value:
            neg_value = "|".split(neg_value)
        else:
            neg_value = [neg_value]

        if 'session_id' in params.keys():
            session_id = params['session_id']
            by = [user_id, session_id]
        else:
            by = [user_id]

        users, items, label = [], [], []                        # 收集users, items, labels
        for group, row in df.groupby(by=by):
            if isinstance(group, tuple):
                group = group[0]
            if len(set(set(pos_value) & set(row[behavior_type].unique().tolist()))) >= 1:
                show_items = row[row[behavior_type].isin(pos_value)][item_id].to_list()
                for pos_i in row[row[behavior_type].isin(neg_value)][item_id].to_list():
                    users.append(group)
                    items.append(pos_i)
                    label.append(1)
                    if len(show_items) > ratio:
                        neg_i = random.choices(show_items, k=ratio)
                    else:
                        neg_i = show_items
                    users.extend([group] * len(neg_i))
                    items.extend(neg_i)
                    label.extend([0] * len(neg_i))
        df = {user_id: users, item_id: items, 'label': label}
        df = pd.DataFrame(df, columns=[user_id, item_id, 'label'])
        return df