from collections import defaultdict, Iterable
import math
from tqdm import tqdm
import numpy as np
import sys
sys.path.append('../../')


class ItemCF(object):
    def __init__(self, model_cfg=None):
        self.sim_item_corr = None
        self.user_item_dict = None
        self.item_cnt = None
        self.item_cnt_mid = None
        self.item_list = []
        self.user_list = []
        self.popular_item_list = []
        self.model_cfg = model_cfg
        self.topN_hist_item = self.model_cfg['topN_hist_item']
        self.topN_final = self.model_cfg['topN_final']

    def fit(self, df):
        user_item_ = df.groupby('user_id')['item_id'].agg(list).reset_index()
        self.user2item = dict(zip(user_item_['user_id'], user_item_['item_id']))
        self.item_list = df['item_id'].unique()
        self.user_list = df['user_id'].unique()
        self.sim_item_corr, self.item_cnt = self.get_sim_item(self.user2item, use_iif=True)
        self.item_cnt_mid = sorted(self.item_cnt.values())
        self.item_cnt_mid = self.item_cnt_mid[len(self.item_cnt_mid) // 2]
        return self.sim_item_corr

    def get_result(self):
        return self.sim_item_corr

    def predict_one(self, user_id, iids, partition_tags=None):
        item_scores = self.predict_one_with_idx_and_score(user_id, iids)
        return [x[0] for x in item_scores]

    def predict_one_with_idx_and_score(self, user_id, iids):
        rank = {}
        interacted_items = iids
        for idx in range(len(interacted_items)):
            i = interacted_items[idx]
            if i not in self.sim_item_corr:
                continue
            w = math.log2(1.46 + self.item_cnt_mid / max(self.item_cnt[i], 1))
            for j, wij in sorted(self.sim_item_corr[i].items(), key=lambda d: d[1], reverse=True)[
                          0:self.topN_hist_item]:
                if j not in interacted_items:
                    rank.setdefault(j, 0)
                    score = max(math.pow((self.item_cnt_mid / max(self.item_cnt[j], 1)), 1.44) * w, 1)
                    rank[j] += wij / np.log(0.666 + min(abs(len(interacted_items) - idx), 91)) * score
        rec_list = sorted(rank.items(), key=lambda d: d[1], reverse=True)[:self.topN_final]
        if len(rec_list)<self.topN_hist_item:
            for i in range(self.topN_hist_item-len(rec_list)):
                rec_list.append((self.popular_item_list[i],0))
        return rec_list

    def get_scores(self, user2hist_items, item_ids):
        scores = []
        for user2hist_item, item_id in tqdm(zip(user2hist_items, item_ids)):
            score = self.get_score(user2hist_item, item_id)
            scores.append(score)
        return scores

    def get_score(self, user2hist_item, item_id):
        score = 0
        interacted_items = user2hist_item
        for idx in range(len(interacted_items)):
            i = interacted_items[idx]
            if i not in self.sim_item_corr:
                continue
            if item_id in self.sim_item_corr[i]:
                w = math.log2(1.46 + self.item_cnt_mid / max(self.item_cnt[i], 1))
                score_sub = max(math.pow((self.item_cnt_mid / max(self.item_cnt[item_id], 1)), 1.44) * w, 1)
                score += self.sim_item_corr[i][item_id] / np.log(
                    0.666 + min(abs(len(interacted_items) - idx), 91)) * score_sub
        return score

    def get_scores_online(self, user2hist_item, item_ids):
        scores = []
        for item_id in item_ids:
            score = self.get_score(user2hist_item, item_id)
            scores.append(score)
        return scores

    def predict_batch(self, user_ids):
        results = dict()
        for user_id in tqdm(user_ids):
            if user_id not in self.user_list:
                results[user_id] = self.popular_item_list[:self.topN_final]
            else:
                results[user_id] = self.predict_one(user_id, iids=self.user2item[user_id])
        return results

    def predict(self, user_ids):
        if isinstance(user_ids, Iterable) and type(user_ids) != str:
            return self.predict_batch(user_ids)
        else:
            if user_ids not in self.user_list:
                return self.popular_item_list[:self.topN_final]
            else:
                return self.predict_one(user_ids, iids=self.user2item[user_ids])

    def get_sim_item(self, user_item_dict, use_iif=False):
        sim_item = {}
        item_cnt = defaultdict(int)
        for user, items in tqdm(user_item_dict.items()):
            items = items[-30:]
            for idx in range(len(items)):
                i = items[idx]
                item_cnt[i] += 1
                sim_item.setdefault(i, {})
                for idx2 in range(len(items)):
                    relate_item = items[idx2]
                    if i == relate_item:
                        continue
                    sim_item[i].setdefault(relate_item, 0)
                    sim_item[i][relate_item] += 1 / np.log2(1 + min(abs(idx - idx2), 66)) / np.log(
                        32 + len(items))
        sim_item_corr = sim_item.copy()
        for i, related_items in tqdm(sim_item.items()):
            for j, cij in related_items.items():
                sim_item_corr[i][j] = cij / math.sqrt((13 + item_cnt[i]) * (13 + item_cnt[j]))
        return sim_item_corr, item_cnt
