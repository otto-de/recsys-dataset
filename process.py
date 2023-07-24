# import json
# import pandas as pd

# data = []

# with open('train.jsonl', 'r') as f:
#     for i, line in enumerate(f):
#         session = json.loads(line)
#         for event in session['events']:
#             event['session'] = session['session']
#             data.append(event)
#         if i == 0:
#             break

# df = pd.DataFrame(data)
# print(df)


import numpy as np
import pandas as pd

from pathlib import Path

data_path = Path('/Users/williamfeng/Desktop/COMP9417/Group Project/otto-recommender-system')

num_lines = sum(1 for line in open(data_path / 'train.jsonl'))
print(f'number of lines in train: {num_lines:_}')

chunksize = 100_000
num_chunks = int(np.ceil(num_lines / 100_000))
print(f'number of chunks: {num_chunks:_}')

n = 2
train_sessions = pd.DataFrame()
chunks = pd.read_json(data_path / 'train.jsonl', lines=True, chunksize=chunksize)

for e, chunk in enumerate(chunks):
    if e < 2:
        train_sessions = pd.concat([train_sessions, chunk])
    else:
        break
train_sessions = train_sessions.set_index('session', drop=True).sort_index()

print(train_sessions)