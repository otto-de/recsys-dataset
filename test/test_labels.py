from src.labels import ground_truth


def test_ground_truth():
    events = [{
        'aid': 1000000,
        'ts': 1000000000001,
        'type': 'clicks'
    }, {
        'aid': 1000001,
        'ts': 1000000000002,
        'type': 'clicks'
    }, {
        'aid': 1000002,
        'ts': 1000000000003,
        'type': 'clicks'
    }, {
        'aid': 1000003,
        'ts': 1000000000004,
        'type': 'clicks'
    }, {
        'aid': 1000000,
        'ts': 1000000000005,
        'type': 'carts'
    }, {
        'aid': 1000004,
        'ts': 1000000000006,
        'type': 'clicks'
    }, {
        'aid': 1000004,
        'ts': 1000000000007,
        'type': 'carts'
    }, {
        'aid': 1000005,
        'ts': 1000000000008,
        'type': 'clicks'
    }, {
        'aid': 1000007,
        'ts': 1000000000009,
        'type': 'clicks'
    }, {
        'aid': 1000007,
        'ts': 1000000000010,
        'type': 'carts'
    }, {
        'aid': 100005,
        'ts': 1000000000011,
        'type': 'carts'
    }, {
        'aid': 1000000,
        'ts': 1000000000012,
        'type': 'orders'
    }, {
        'aid': 1000004,
        'ts': 1000000000012,
        'type': 'orders'
    }, {
        'aid': 1000007,
        'ts': 1000000000013,
        'type': 'clicks'
    }, {
        'aid': 1000007,
        'ts': 1000000000014,
        'type': 'carts'
    }]

    expected = [{
        'aid': 1000000,
        'ts': 1000000000001,
        'type': 'clicks',
        'labels': {
            'clicks': 1000001,
            'carts': set([1000000, 1000004, 1000007, 100005]),
            'orders': set([1000000, 1000004])
        }
    }, {
        'aid': 1000001,
        'ts': 1000000000002,
        'type': 'clicks',
        'labels': {
            'clicks': 1000002,
            'carts': set([1000000, 1000004, 1000007, 100005]),
            'orders': set([1000000, 1000004])
        }
    }, {
        'aid': 1000002,
        'ts': 1000000000003,
        'type': 'clicks',
        'labels': {
            'clicks': 1000003,
            'carts': set([1000000, 1000004, 1000007, 100005]),
            'orders': set([1000000, 1000004])
        }
    }, {
        'aid': 1000003,
        'ts': 1000000000004,
        'type': 'clicks',
        'labels': {
            'clicks': 1000004,
            'carts': set([1000000, 1000004, 1000007, 100005]),
            'orders': set([1000000, 1000004])
        }
    }, {
        'aid': 1000000,
        'ts': 1000000000005,
        'type': 'carts',
        'labels': {
            'clicks': 1000004,
            'carts': set([1000004, 1000007, 100005]),
            'orders': set([1000000, 1000004])
        }
    }, {
        'aid': 1000004,
        'ts': 1000000000006,
        'type': 'clicks',
        'labels': {
            'clicks': 1000005,
            'carts': set([1000004, 1000007, 100005]),
            'orders': set([1000000, 1000004])
        }
    }, {
        'aid': 1000004,
        'ts': 1000000000007,
        'type': 'carts',
        'labels': {
            'clicks': 1000005,
            'carts': set([1000007, 100005]),
            'orders': set([1000000, 1000004])
        }
    }, {
        'aid': 1000005,
        'ts': 1000000000008,
        'type': 'clicks',
        'labels': {
            'clicks': 1000007,
            'carts': set([1000007, 100005]),
            'orders': set([1000000, 1000004])
        }
    }, {
        'aid': 1000007,
        'ts': 1000000000009,
        'type': 'clicks',
        'labels': {
            'clicks': 1000007,
            'carts': set([1000007, 100005]),
            'orders': set([1000000, 1000004])
        }
    }, {
        'aid': 1000007,
        'ts': 1000000000010,
        'type': 'carts',
        'labels': {
            'clicks': 1000007,
            'carts': set([100005, 1000007]),
            'orders': set([1000000, 1000004])
        }
    }, {
        'aid': 100005,
        'ts': 1000000000011,
        'type': 'carts',
        'labels': {
            'clicks': 1000007,
            'carts': set([1000007]),
            'orders': set([1000000, 1000004])
        }
    }, {
        'aid': 1000000,
        'ts': 1000000000012,
        'type': 'orders',
        'labels': {
            'clicks': 1000007,
            'carts': set([1000007]),
            'orders': set([1000004])
        }
    }, {
        'aid': 1000004,
        'ts': 1000000000012,
        'type': 'orders',
        'labels': {
            'clicks': 1000007,
            'carts': set([1000007])
        }
    }, {
        'aid': 1000007,
        'ts': 1000000000013,
        'type': 'clicks',
        'labels': {
            'carts': set([1000007]),
        }
    }]

    result = ground_truth(events)
    assert result == expected
