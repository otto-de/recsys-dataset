<div align="center">

# OTTO Recommender Systems Dataset

[![GitHub Stars](https://img.shields.io/github/stars/otto-de/recsys-dataset.svg?style=for-the-badge&color=yellow)](https://github.com/otto-de/recsys-dataset)
[![License: MIT](https://img.shields.io/github/license/otto-de/recsys-dataset?style=for-the-badge)](LICENSE)
[![Kaggle Competition](https://img.shields.io/badge/kaggle-competition-20BEFF?style=for-the-badge&logo=kaggle)](https://www.kaggle.com/competitions/otto-recommender-system)
[![OTTO](https://img.shields.io/badge/otto-jobs-F00020?style=for-the-badge&logo=otto)](https://www.otto.de/jobs/technology/ueberblick/)

**A real-world e-commerce dataset for multi-objective recommender systems research.**

<img src=".readme/header.png" width="100%">

---
<p align="center">
  <a href="#get-the-data">Get the Data</a> •
  <a href="#data-format">Data Format</a> •
  <a href="#evaluation">Evaluation</a> •
  <a href="#faq">FAQ</a> •
  <a href="#license">License</a>
</p>

</div>

The `OTTO` session dataset is a large-scale dataset intended for multi-objective recommendation research. We collected the data from anonymized behavior logs of the [OTTO](https://otto.de) webshop and the app. The mission of this dataset is to serve as a benchmark for session-based recommendations and foster research in the multi-objective and session-based recommender systems area. We also launched a [Kaggle competition](https://www.kaggle.com/competitions/otto-recommender-system) with the goal to predict clicks, cart additions, and orders based on previous events in a user session.

## Key Features

- 12M real-world anonymized user sessions
- 220M events, consiting of `clicks`, `carts` and `orders`
- 1.8M unique articles in the catalogue
- Ready to use data in `.jsonl` format
- Evaluation metrics for multi-objective optimization

## Dataset Statistics

| Dataset |  #sessions |    #items |     #events |     #clicks |     #carts |   #orders | Density [%] |
| :------ | ---------: | --------: | ----------: | ----------: | ---------: | --------: | ----------: |
| Train   | 12.899.779 | 1.855.603 | 216.716.096 | 194.720.954 | 16.896.191 | 5.098.951 |      0.0005 |
| Test    |  1.671.803 |       TBA |         TBA |         TBA |        TBA |       TBA |         TBA |

|                           |  mean |   std |  min |  50% |  75% |  90% |  95% |  max |
| :------------------------ | ----: | ----: | ---: | ---: | ---: | ---: | ---: | ---: |
| Train #events per session | 16.80 | 33.58 |    2 |    6 |   15 |   39 |   68 |  500 |
| Test #events per session  |   TBA |   TBA |  TBA |  TBA |  TBA |  TBA |  TBA |  TBA |

<details>
    <summary><strong>#events per session histogram (90th percentile)</strong></summary>
    <img src=".readme/events_per_session_p90.svg" width="800px">
</details>

|                        |   mean |    std |  min |  50% |  75% |  90% |  95% |    max |
| :--------------------- | -----: | -----: | ---: | ---: | ---: | ---: | ---: | -----: |
| Train #events per item | 116.79 | 728.85 |    3 |   20 |   56 |  183 |  398 | 129004 |
| Test #events per item  |    TBA |    TBA |  TBA |  TBA |  TBA |  TBA |  TBA |    TBA |

<details>
    <summary><strong>#events per item histogram (90th percentile)</strong></summary>
    <img src=".readme/events_per_item_p90.svg" width="800px">
</details>

**Note:** The full test set is not yet available. We will update the tables once the Kaggle competition is over and the test set is released.

## Get the Data

The data is stored on the [Kaggle](https://www.kaggle.com/competitions/otto-recommender-system/data) platform and can be downloaded using their API:

```Shell
kaggle competitions download -c otto-recommender-system
```

## Data Format

The sessions are stored as `JSON` objects containing a unique `session` ID and a list of `events`:

```JSON
{
    "session": 42,
    "events": [
        { "aid": 0, "ts": 1661200010000, "type": "clicks" },
        { "aid": 1, "ts": 1661200020000, "type": "clicks" },
        { "aid": 2, "ts": 1661200030000, "type": "clicks" },
        { "aid": 2, "ts": 1661200040000, "type": "carts"  },
        { "aid": 3, "ts": 1661200050000, "type": "clicks" },
        { "aid": 3, "ts": 1661200060000, "type": "carts"  },
        { "aid": 4, "ts": 1661200070000, "type": "clicks" },
        { "aid": 2, "ts": 1661200080000, "type": "orders" },
        { "aid": 3, "ts": 1661200080000, "type": "orders" }
    ]
}
```

- `session` - the unique session id
- `events` - the time ordered sequence of events in the session
  - `aid` - the article id (product code) of the associated event
  - `ts` - the Unix timestamp of the event
  - `type` - the event type, i.e., whether a product was clicked, added to the user's cart, or ordered during the session

## Submission Format

For each `session` id and `type` combination in the test set, you must predict the `aid` values in the `label` column, which is space delimited. You can predict up to 20 `aid` values per row. The file should contain a header and have the following format:

```CSV
session_type,labels
42_clicks,0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
42_carts,0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
42_orders,0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
```

## Prerequisites and Installation

To run our scripts, you need to have [Python 3](https://www.python.org/downloads/) and [Pipenv](https://pipenv.pypa.io/en/latest/) installed. Then, you can install the dependencies with:

```bash
pipenv sync
```

## Evaluation

Submissions are evaluated on [Recall](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)#Recall)@20 for each action `type`, and the three recall values are weight-averaged:

$$
score = 0.10 \cdot R_{clicks} + 0.30 \cdot R_{carts} + 0.60 \cdot R_{orders}
$$

where $R$ is defined as

$$
R_{type} = \frac{ \sum\limits_{i=1}^N | \\{ \text{predicted aids} \\}\_{i, type} \cap \\{ \text{ground truth aids} \\}\_{i, type} | }{ \sum\limits_{i=1}^N \min{( 20, | \\{ \text{ground truth aids} \\}_{i, type} | )}}
$$

and $N$ is the total number of sessions in the test set, and $\text{predicted aids}$ are the predictions for each session-type (e.g., each row in the submission file) _truncated after the first 20 predictions_.

For each `session` in the test data, your task it to predict the `aid` values for each `type` that occur after the last timestamp `ts` the test session. In other words, the test data contains sessions truncated by timestamp, and you are to predict what occurs after the point of truncation.

For `clicks` there is only a single ground truth value for each session, which is the next `aid` clicked during the session (although you can still predict up to 20 `aid` values). The ground truth for `carts` and `orders` contains all `aid` values that were added to a cart and ordered respectively during the session.

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

To create these labels from unlabeled sessions, you can use the function, `ground_truth` in [labels.py](src/labels.py).

### Train/Test Split

Since we want to evaluate a model's performance in the future, as would be the case when we deploy such a system in an actual webshop, we choose a time-based validation split. Our train set consists of observations from 4 weeks, while the test set contains user sessions from the following week. Furthermore, we trimmed train sessions overlapping with the test period, as depicted in the following diagram, to prevent information leakage from the future:

<div align="center">
  <img src=".readme/train_test_split.png" width="100%">
</div>

We will publish the final test set after the Kaggle [competition](https://www.kaggle.com/competitions/otto-recommender-system) is finalized. However, until then, participants of the competition can create their truncated test sets from the training sessions and use this to evaluate their models offline. For this purpose, we include a Python script called `testset.py`:

```Shell
pipenv run python -m src.testset --train-set train.jsonl --days 2 --output-path 'out/' --seed 42 
```

### Metrics Calculation

You can use the `evalute.py` script to calculate the Recall@20 for each action type and the weighted average Recall@20 for your submission:

```Shell
pipenv run python -m src.evaluate --test-labels test_labels.jsonl --predictions predictions.csv
```

## FAQ

### How is a user `session` defined?

- A session is all activity by a single user either in the train or the test set.

### Are you allowed to train on the truncated test sessions?

- Yes, for the scope of the competition, you may use all the data we provided.

### How is Recall@20 calculated if the ground truth contains more than 20 labels?

- If you predict 20 items correctly out of the ground truth labels, you will still score 1.0.

## License

The OTTO dataset is released under the [CC-BY 4.0 License](https://creativecommons.org/licenses/by/4.0/), while the code is licensed under the [MIT License](LICENSE).

## Citation

BibTeX entry:

```BibTeX
@online{normann2022ottodataset,
  author       = {Philipp Normann, Sophie Baumeister, Timo Wilm},
  title        = {OTTO Recommender Systems Dataset: A real-world dataset of anonymized e-commerce sessions for multi-objective recommendation research},
  date         = {2022-11-01},
}
```
