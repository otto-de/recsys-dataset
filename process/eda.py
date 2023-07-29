# This file is solely for Exploratory Data Analysis (EDA) purposes.

import pandas as pd
from pathlib import Path
pd.set_option("display.max_columns", None)
data_path = Path(
    '../test/resources')

train_df = pd.DataFrame()
sample_size = 100_000
chunks = pd.read_json(data_path / 'otto-recsys-train.jsonl',
                      lines=True, chunksize=sample_size)

for chunk in chunks:
    event_dict = {'session': [], 'aid': [], 'ts': [], 'type': []}

    for session, events in zip(chunk['session'].tolist(), chunk['events'].tolist()):
        for event in events:
            event_dict['session'].append(session)
            event_dict['aid'].append(event['aid'])
            event_dict['ts'].append(event['ts'])
            event_dict['type'].append(event['type'])
    train_df = pd.DataFrame(event_dict)

    break

train_df = train_df.reset_index(drop=True)
train_df["minutes"] = train_df[["session", "ts"]
                               ].groupby("session").diff(-1)*(-1/1000/60)
print("\nTraining data\n")
print(train_df)

temp = train_df.groupby(['type', 'aid'])['session'].agg('count').reset_index()
temp.columns = ['type', 'aid', 'count']
order_num_df = temp.loc[(temp['type'] == 'orders'), ]
order_num_df = order_num_df.sort_values(
    ['count'], ascending=False).reset_index()

order_num_df.aid = ' ' + order_num_df.aid.astype('str')
best_sold_list = order_num_df[:20].aid.sum()
print("\nBest sold items\n")
print(best_sold_list)

test_df = pd.DataFrame()
chunks = pd.read_json(data_path / 'otto-recsys-test.jsonl',
                      lines=True, chunksize=sample_size)

for chunk in chunks:
    event_dict = {'session': [], 'aid': [], 'ts': [], 'type': []}
    for session, events in zip(chunk['session'].tolist(), chunk['events'].tolist()):
        for event in events:
            event_dict['session'].append(session)
            event_dict['aid'].append(event['aid'])
            event_dict['ts'].append(event['ts'])
            event_dict['type'].append(event['type'])
    chunk_session = pd.DataFrame(event_dict)
    test_df = pd.concat([test_df, chunk_session])

test_df = test_df.reset_index(drop=True)
test_df["minutes"] = test_df[["session", "ts"]
                             ].groupby("session").diff(-1) * (-1 / 1000 / 60)
test_df = test_df.sort_values(['minutes'], ascending=False)

test_action_df = test_df.copy()
test_action_df.aid = ' ' + test_df.aid.astype('str')
test_action_df = test_action_df.groupby(['session', 'type'])[
    'aid'].sum().reset_index()
print("\nTesting data\n")
print(test_action_df)

next_clicks_df = pd.DataFrame(
    test_action_df.loc[(test_action_df["type"] == 'clicks'), ]).copy()
print("\nRecommended clicks\n")
print(next_clicks_df)

next_orders_df = pd.DataFrame(
    test_action_df.loc[(test_action_df["type"] == 'carts'), ])
# Recommending clicked items instead of most sold items increased the score
next_orders_df = pd.merge(next_orders_df, next_clicks_df[[
                          'session', 'aid']], on='session', how='left')
next_orders_df["aid"] = next_orders_df["aid_x"] + next_orders_df["aid_y"]
next_orders_df = next_orders_df.drop(['aid_x', 'aid_y'], axis=1)
next_orders_df['type'] = 'orders'
print("\nRecommended orders\n")
print(next_orders_df)

next_carts_df = pd.DataFrame(
    test_action_df.loc[(test_action_df["type"] == 'clicks'), ])
next_carts_df['type'] = 'carts'
print("\nRecommended carts\n")
print(next_carts_df)

recommend_df = pd.concat(
    [next_orders_df, next_carts_df, next_clicks_df], axis=0)
recommend_df["session_type"] = recommend_df["session"].astype(
    'str') + "_" + recommend_df["type"]
print("\nRecommendations overall\n")
print(recommend_df)

sample_sub = pd.read_csv(data_path / 'sample_submission.csv')
sample_sub = pd.merge(sample_sub, recommend_df[[
                      "session_type", "aid"]], on="session_type", how="left")
sample_sub['next'] = sample_sub['aid'] + best_sold_list
sample_sub['next'].fillna(best_sold_list, inplace=True)
sample_sub['next'] = sample_sub['next'].str.strip()
sample_sub = sample_sub.drop(["labels", "aid"], axis=1)
sample_sub.columns = ("session_type", "labels")
sample_sub.to_csv('predictions.csv', index=False)
