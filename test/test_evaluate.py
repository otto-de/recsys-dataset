from src.evaluate import (evaluate_session, evaluate_sessions, get_scores,
                          num_events, recall_by_event_type, weighted_recalls)


def test_evaluate_session():
    label_last_event = {
        'clicks': 1000003,
        'carts': set([1000000, 1000004, 1000007, 100005]),
        'orders': set([1000000, 1000004])
    }
    prediction = {
        "clicks": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "carts": [1000004, 0, 1, 2, 3, 4, 5, 6, 7, 8],
        "orders": [1000000, 0, 1, 2, 3, 4, 5, 6, 7, 8]
    }
    expected_hits = {"clicks": 0, "carts": 1, "orders": 1}
    assert expected_hits == evaluate_session(
        label_last_event, prediction, k=20)

    label_last_event = {'clicks': 1000003, 'carts': set(
        [1000000, 1000004, 1000007, 100005]), "orders": set()}
    prediction = {
        "clicks": [1000003, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "carts": [1000004, 0, 1, 2, 3, 4, 5, 6, 7, 8],
        "orders": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    expected_hits = {"clicks": 1, "carts": 1, "orders": None}
    assert expected_hits == evaluate_session(
        label_last_event, prediction, k=20)

    label_last_event = {'clicks': 1000003, 'orders': set([1000000, 1000004])}
    prediction = {
        "clicks": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "carts": [1000004, 0, 1, 2, 3, 4, 5, 6, 7, 8],
        "orders": [1000000, 0, 1, 2, 3, 4, 5, 6, 7, 8]
    }
    expected_hits = {"clicks": 0, "carts": None, "orders": 1}
    assert expected_hits == evaluate_session(
        label_last_event, prediction, k=20)

    label_last_event = {'clicks': 1, 'orders': set(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])}
    prediction = {
        "clicks": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "carts": [1000004, 0, 1, 2, 3, 4, 5, 6, 7, 8],
        "orders": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    expected_hits = {"clicks": 1, "carts": None, "orders": 10}
    assert expected_hits == evaluate_session(
        label_last_event, prediction, k=10)

    label_last_event = {'clicks': None, 'carts': set(), 'orders': set(
        [0, 1, 2, 3, 4, 5, 16, 17, 18, 19, 20])}
    prediction = {
        "clicks": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "carts": [1000004, 0, 1, 2, 3, 4, 5, 6, 7, 8],
        "orders": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    }
    expected_hits = {"clicks": None, "carts": None, "orders": 6}
    assert expected_hits == evaluate_session(
        label_last_event, prediction, k=10)


def test_evaluate_sessions():
    k = 3
    predictions = {
        1: {
            "clicks": [1, 2, 3],
            "carts": [1, 2, 3],
            "orders": [1, 32, 33]
        },
        2: {
            "clicks": [1000003, 2, 3],
            "carts": [1000004, 2, 3, 1000007],
            "orders": [1, 2, 3]
        },
        3: {
            "clicks": [1, 2, 3],
            "carts": [1000007, 1000004, 3],
            "orders": [1, 2, 3]
        }}
    labels = {
        1: {
            'clicks': None,
            'carts': set(),
            'orders': set([0, 1, 2, 3, 4, 5, 16, 17, 18, 19, 20])
        },
        2: {
            'clicks': 1000003,
            'carts': set([1000000, 1000004, 1000007]),
            'orders': set([1000000, 1000004])
        },
        3: {
            'clicks': 1000003,
            'carts': set([1000000, 1000004, 1000007]),
            "orders": set()
        },
        4: {
            'clicks': 1000003,
            'carts': set([1000000, 1000004, 1000007]),
            "orders": set()
        }
    }

    expected = {
        1: {
            'clicks': None,
            'carts': None,
            'orders': 1
        },
        2: {
            'clicks': 1,
            'carts': 1,
            'orders': 0
        },
        3: {
            'clicks': 0,
            'carts': 2,
            "orders": None
        },
        4: {
            'clicks': 0,
            'carts': 0,
            "orders": None
        }
    }

    assert expected == evaluate_sessions(labels, predictions, k)


def test_num_events():
    k = 10
    labels = {
        1: {
            'clicks': None,
            'carts': set(),
            'orders': set([0, 1, 2, 3, 4, 5, 16, 17, 18, 19, 20])
        },
        2: {
            'clicks': 1000003,
            'carts': set([1000000, 1000004, 1000007]),
            'orders': set([1000000, 1000004])
        },
        3: {
            'clicks': 1000003,
            'carts': set([1000000, 1000004, 1000007]),
            "orders": set()
        },
        4: {
            'clicks': 1000003,
            'carts': set([1000000, 1000004, 1000007]),
            "orders": set()
        }
    }

    expected = {'clicks': 3, 'carts': 9, 'orders': 12}

    assert expected == num_events(labels, k)


def test_recall_by_event_type():

    total_number_events = {'clicks': 3, 'carts': 10, 'orders': 4}

    elementwise_evaluation = {
        1: {
            'clicks': None,
            'carts': None,
            'orders': 1
        },
        2: {
            'clicks': 1,
            'carts': 1,
            'orders': 0
        },
        3: {
            'clicks': 0,
            'carts': 2,
            "orders": None
        },
        4: {
            'clicks': 0,
            'carts': 0,
            "orders": None
        }
    }

    expected_recall = {
        'clicks': (1 + 0 + 0) / total_number_events["clicks"],
        'carts': (1 + 2 + 0) / total_number_events["carts"],
        'orders': (1 + 0) / total_number_events["orders"]
    }

    assert expected_recall == recall_by_event_type(
        elementwise_evaluation, total_number_events)


def test_weighted_recalls():
    recalls = {'clicks': 0.6, 'carts': 0.4, 'orders': 0.3}
    weights = {'clicks': 0.1, 'carts': 0.3, 'orders': 0.7}
    recall = 0.6 * 0.1 + 0.4 * 0.3 + 0.3 * 0.7
    assert recall == weighted_recalls(recalls, weights)


def test_get_scores():
    k = 3
    weights = {'clicks': 0.1, 'carts': 0.3, 'orders': 0.6}
    predictions = {
        1: {
            "clicks": [1, 2, 3],
            "carts": [1, 2, 3],
            "orders": [1, 32, 33]
        },
        2: {
            "clicks": [1000003, 2, 3],
            "carts": [1000004, 2, 3, 1000007],
            "orders": [1, 2, 3]
        },
        3: {
            "clicks": [1, 2, 3],
            "carts": [1000007, 1000004, 3],
            "orders": [1, 2, 3]
        }}
    labels = {
        1: {
            'clicks': None,
            'carts': set(),
            'orders': set([0, 1, 2, 3, 4, 5, 16, 17, 18, 19, 20])
        },
        2: {
            'clicks': 1000003,
            'carts': set([1000000, 1000004, 1000007]),
            'orders': set([1000000, 1000004])
        },
        3: {
            'clicks': 1000003,
            'carts': set([1000000, 1000004, 1000007]),
            "orders": set()
        },
        4: {
            'clicks': 1000003,
            'carts': set([1000000, 1000004, 1000007]),
            "orders": set()
        }
    }

    expected_evaluated_events = {
        1: {
            'clicks': None,
            'carts': None,
            'orders': 1
        },
        2: {
            'clicks': 1,
            'carts': 1,
            'orders': 0
        },
        3: {
            'clicks': 0,
            'carts': 2,
            "orders": None
        },
        4: {
            'clicks': 0,
            'carts': 0,
            "orders": None
        }
    }

    expected_recalls = {"clicks": 1 / 3, "carts": 3 / 9, "orders": 1 / 5}
    expected_scores = {
        "clicks": 1 / 3,
        "carts": 3 / 9,
        "orders": 1 / 5,
        "total": weights["clicks"] * expected_recalls["clicks"] +
        weights["carts"] * expected_recalls["carts"] +
        weights["orders"] * expected_recalls["orders"]
    }
    assert expected_evaluated_events == evaluate_sessions(
        labels, predictions, k)
    assert expected_scores == get_scores(labels, predictions, k, weights)
