import json
from pathlib import Path

import pandas as pd
from src.testset import split_events, train_test_split


def test_split_events_short():
    events_short = [{
        'aid': 1,
        'ts': 1000000000001,
        'type': 'clicks'
    }, {
        'aid': 2,
        'ts': 1000000000002,
        'type': 'clicks'
    }]

    result = split_events(events_short)

    expected_events = [{'aid': 1, 'ts': 1000000000001, 'type': 'clicks'}]
    expected_labels = {'clicks': 2}

    assert result[0] == expected_events
    assert result[1] == expected_labels


def test_split_events_long():
    events_long = [{
        'aid': 1,
        'ts': 1000000000001,
        'type': 'clicks'
    }, {
        'aid': 1,
        'ts': 1000000000002,
        'type': 'carts'
    }, {
        'aid': 1,
        'ts': 1000000000003,
        'type': 'orders'
    }, {
        'aid': 2,
        'ts': 1000000000004,
        'type': 'clicks'
    }]

    result = split_events(events_long, 1)
    expected_events = [{'aid': 1, 'ts': 1000000000001, 'type': 'clicks'}]
    expected_labels = {'clicks': 2, 'carts': set([1]), 'orders': set([1])}
    print(result)
    assert result[0] == expected_events
    assert result[1] == expected_labels

    result = split_events(events_long, 2)
    expected_events = [{
        'aid': 1,
        'ts': 1000000000001,
        'type': 'clicks'
    }, {
        'aid': 1,
        'ts': 1000000000002,
        'type': 'carts'
    }]
    expected_labels = {'clicks': 2, 'orders': set([1])}
    assert result[0] == expected_events
    assert result[1] == expected_labels

    result = split_events(events_long, 3)
    expected_events = [{
        'aid': 1,
        'ts': 1000000000001,
        'type': 'clicks'
    }, {
        'aid': 1,
        'ts': 1000000000002,
        'type': 'carts'
    }, {
        'aid': 1,
        'ts': 1000000000003,
        'type': 'orders'
    }]
    expected_labels = {'clicks': 2}
    assert result[0] == expected_events
    assert result[1] == expected_labels


def test_train_test_split():
    train_file = Path('test/resources/output/train.jsonl')
    test_file = Path('test/resources/output/test.jsonl')
    train_chunks = pd.read_json('test/resources/train.jsonl', lines=True, chunksize=10)
    max_ts = 1661723994936
    test_days = 7
    train_items = set()
    train_test_split(train_chunks, train_file, test_file, max_ts, test_days, 2)
    with open(train_file, 'r') as f:
        train_lines = f.readlines()
        assert len(train_lines) == 10
        for line in train_lines:
            session = json.loads(line)
            assert len(session['events']) >= 2
            for event in session['events']:
                train_items.add(event['aid'])
                # assert no timestamp in train set is smaller than max_ts - test_days
                assert event['ts'] < max_ts - test_days * 24 * 60 * 60 * 1000
    with open(test_file, 'r') as f:
        test_lines = f.readlines()
        assert len(test_lines) == 8
        for line in test_lines:
            session = json.loads(line)
            assert len(session['events']) >= 2
            for event in session['events']:
                # assert all items in test set are also in train set
                assert event['aid'] in train_items
                # assert all timestamp in test set are greater than max_ts - test_days
                assert event['ts'] > max_ts - test_days * 24 * 60 * 60 * 1000
