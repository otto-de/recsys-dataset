# pipenv run python -m testset --train-set ../test/resources/train.jsonl --days 2 --output-path 'out/' --seed 42

import argparse
import json
import random
from copy import deepcopy
from pathlib import Path

import pandas as pd
from beartype import beartype
from pandas.io.json._json import JsonReader
from tqdm.auto import tqdm

from labels import ground_truth


class setEncoder(json.JSONEncoder):

    def default(self, obj):
        return list(obj)


@beartype
def split_events(events: list[dict], split_idx=None):
    test_events = ground_truth(deepcopy(events))
    if not split_idx:
        split_idx = random.randint(1, len(test_events))
    test_events = test_events[:split_idx]
    labels = test_events[-1]['labels']
    for event in test_events:
        del event['labels']
    return test_events, labels


@beartype
def create_kaggle_testset(sessions: pd.DataFrame, sessions_output: Path, labels_output: Path):
    last_labels = []
    splitted_sessions = []

    for _, session in tqdm(sessions.iterrows(), desc="Creating trimmed testset", total=len(sessions)):
        session = session.to_dict()
        splitted_events, labels = split_events(session['events'])
        last_labels.append({'session': session['session'], 'labels': labels})
        splitted_sessions.append({'session': session['session'], 'events': splitted_events})

    with open(sessions_output, 'w') as f:
        for session in splitted_sessions:
            f.write(json.dumps(session) + '\n')

    with open(labels_output, 'w') as f:
        for label in last_labels:
            f.write(json.dumps(label, cls=setEncoder) + '\n')


@beartype
def trim_session(session: dict, max_ts: int) -> dict:
    session['events'] = [event for event in session['events'] if event['ts'] < max_ts]
    return session


@beartype
def get_max_ts(sessions_path: Path) -> int:
    max_ts = float('-inf')
    with open(sessions_path) as f:
        for line in tqdm(f, desc="Finding max timestamp"):
            session = json.loads(line)
            max_ts = max(max_ts, session['events'][-1]['ts'])
    return max_ts


@beartype
def filter_unknown_items(session_path: Path, known_items: set[int]):
    filtered_sessions = []
    with open(session_path) as f:
        for line in tqdm(f, desc="Filtering unknown items"):
            session = json.loads(line)
            session['events'] = [event for event in session['events'] if event['aid'] in known_items]
            if len(session['events']) >= 2:
                filtered_sessions.append(session)
    with open(session_path, 'w') as f:
        for session in filtered_sessions:
            f.write(json.dumps(session) + '\n')


@beartype
def train_test_split(session_chunks: JsonReader, train_path: Path, test_path: Path, max_ts: int, test_days: int):
    split_millis = test_days * 24 * 60 * 60 * 1000
    split_ts = max_ts - split_millis
    train_items = set()
    Path(train_path).parent.mkdir(parents=True, exist_ok=True)
    train_file = open(train_path, "w")
    Path(test_path).parent.mkdir(parents=True, exist_ok=True)
    test_file = open(test_path, "w")
    for chunk in tqdm(session_chunks, desc="Splitting sessions"):
        for _, session in chunk.iterrows():
            session = session.to_dict()
            if session['events'][0]['ts'] > split_ts:
                test_file.write(json.dumps(session) + "\n")
            else:
                session = trim_session(session, split_ts)
                if len(session['events']) >= 2:
                    train_items.update([event['aid'] for event in session['events']])
                    train_file.write(json.dumps(session) + "\n")
    train_file.close()
    test_file.close()
    filter_unknown_items(test_path, train_items)


@beartype
def main(train_set: Path, output_path: Path, days: int, seed: int):
    random.seed(seed)
    max_ts = get_max_ts(train_set)

    session_chunks = pd.read_json(train_set, lines=True, chunksize=100000)
    train_file = output_path / 'train_sessions.jsonl'
    test_file_full = output_path / 'test_sessions_full.jsonl'
    train_test_split(session_chunks, train_file, test_file_full, max_ts, days)

    test_sessions = pd.read_json(test_file_full, lines=True)
    test_sessions_file = output_path / 'test_sessions.jsonl'
    test_labels_file = output_path / 'test_labels.jsonl'
    create_kaggle_testset(test_sessions, test_sessions_file, test_labels_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-set', type=Path, required=True)
    parser.add_argument('--output-path', type=Path, required=True)
    parser.add_argument('--days', type=int, default=2)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    main(args.train_set, args.output_path, args.days, args.seed)
