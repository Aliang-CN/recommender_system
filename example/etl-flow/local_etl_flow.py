from dask.threaded import get

from behavior_etl import behavior_etl
from item_etl import item_etl
from join_etl import join_etl
from user_etl import user_etl
from rank_sample_maker import rank_sample_maker
from recall_sample_maker import recall_sample_maker
from rank_train import rank_train
from recall_train import recall_train


def end(params):
    print("etl end")


if __name__ == '__main__':
    params = ['', '1', '']
    dag = {
        'item_etl': (item_etl, params),
        'user_etl': (user_etl, params),
        'behavior_etl': (behavior_etl, params),
        'join_etl': (join_etl, ['item_etl', 'user_etl', 'behavior_etl']),
        'rank_sample_maker': (rank_sample_maker, 'join_etl'),
        'rank_train': (rank_train, 'rank_sample_maker'),
        'recall_sample_maker': (recall_sample_maker, 'join_etl'),
        'recall_train': (recall_train, 'recall_sample_maker'),
        'end': (end, ['rank_train', 'recall_train'])
    }
    print(get(dag, 'end'))
