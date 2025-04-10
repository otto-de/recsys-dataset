# OTTO Recommender System Competition

This document provides guidance for working with the OTTO dataset in the context of the [Kaggle competition](https://www.kaggle.com/competitions/otto-recommender-system), which ended in 2023. The competition focused on multi-objective session-based recommendation, where participants predicted user clicks, cart additions, and orders.

## Submission Format

For each `session` id and `type` combination in the test set, you must predict the `aid` values in the `label` column, which is space delimited. You can predict up to 20 `aid` values per row. The file should contain a header and have the following format:

```CSV
session_type,labels
42_clicks,0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
42_carts,0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
42_orders,0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
```

## Installation

To run our scripts, you need to have [Python 3](https://www.python.org/downloads/) and [Pipenv](https://pipenv.pypa.io/en/latest/) installed. Then, you can install the dependencies with:

```bash
pipenv sync
```

## Evaluation

Submissions are evaluated on [Recall](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)#Recall)@20 for each action `type`, and the three recall values are weight-averaged:

$$
score = 0.10 \cdot R_{clicks} + 0.30 \cdot R_{carts} + 0.60 \cdot R_{orders}
$$

where $R$ is defined as:

$$
R_{type} = \frac{ \sum\limits_{i=1}^N | \\\{ \text{predicted aids} \\\}\_{i, type} \cap \\\{ \text{ground truth aids} \\\}\_{i, type} | }{ \sum\limits_{i=1}^N \min{( 20, | \\\{ \text{ground truth aids} \\\}_{i, type} | )}}
$$

and $N$ is the total number of sessions in the test set, and $\text{predicted aids}$ are the predictions for each session-type (e.g., each row in the submission file) _truncated after the first 20 predictions_.

For each `session` in the test data, your task is to predict the `aid` values for each `type` that occur after the last timestamp `ts` in the test session. In other words, the test data contains sessions truncated by timestamp, and you are to predict what occurs after the point of truncation.

For `clicks`, there is only a single ground truth value for each session, which is the next `aid` clicked during the session (although you can still predict up to 20 `aid` values). The ground truth for `carts` and `orders` contains all `aid` values that were added to a cart and ordered respectively during the session.

<img src=".readme/ground_truth.png" width="100%">

<details>
  <summary><strong>Click here to see the labeled session as <code>JSON</code> from above</strong></summary>

```JSON
[
    {
        "aid": 0,
        "ts": 1661200010000,
        "type": "clicks",
        "labels": {
            "clicks": 1,
            "carts": [2, 3],
            "orders": [2, 3]
        }
    },
    {
        "aid": 1,
        "ts": 1661200020000,
        "type": "clicks",
        "labels": {
            "clicks": 2,
            "carts": [2, 3],
            "orders": [2, 3]
        }
    },
    {
        "aid": 2,
        "ts": 1661200030000,
        "type": "clicks",
        "labels": {
            "clicks": 3,
            "carts": [2, 3],
            "orders": [2, 3]
        }
    },
    {
        "aid": 2,
        "ts": 1661200040000,
        "type": "carts",
        "labels": {
            "clicks": 3,
            "carts": [3],
            "orders": [2, 3]
        }
    },
    {
        "aid": 3,
        "ts": 1661200050000,
        "type": "clicks",
        "labels": {
            "clicks": 4,
            "carts": [3],
            "orders": [2, 3]
        }
    },
    {
        "aid": 3,
        "ts": 1661200060000,
        "type": "carts",
        "labels": {
            "clicks": 4,
            "orders": [2, 3]
        }
    },
    {
        "aid": 4,
        "ts": 1661200070000,
        "type": "clicks",
        "labels": {
            "orders": [2, 3]
        }
    },
    {
        "aid": 2,
        "ts": 1661200080000,
        "type": "orders",
        "labels": {
            "orders": [3]
        }
    }
]
```

</details>

To create these labels from unlabeled sessions, you can use the function `ground_truth` in [labels.py](src/labels.py).

## Train/Test Split

The final test set has been published following the conclusion of the Kaggle [competition](https://www.kaggle.com/competitions/otto-recommender-system). You can access the complete dataset [here](https://www.kaggle.com/datasets/otto/recsys-dataset). Participants of the competition could create their truncated test sets from the training sessions to evaluate their models offline. For this purpose, we include a Python script called `testset.py`:

```Shell
pipenv run python -m src.testset --train-set train.jsonl --days 2 --output-path 'out/' --seed 42 
```

## Metrics Calculation

You can use the `evaluate.py` script to calculate the Recall@20 for each action type and the weighted average Recall@20 for your submission:

```Shell
pipenv run python -m src.evaluate --test-labels test_labels.jsonl --predictions predictions.csv
```

## FAQ

### Are you allowed to train on the truncated test sessions?

- Yes, for the scope of the competition, you may use all the data we provided.

### How is Recall@20 calculated if the ground truth contains more than 20 labels?

- If you predict 20 items correctly out of the ground truth labels, you will still score 1.0.

### Where can I find item and user metadata?

- This dataset intentionally only contains anonymized IDs. Given its already large size, we deliberately did not include content features to make the dataset more manageable and focus on collaborative filtering techniques that solve the multi-objective problem.
