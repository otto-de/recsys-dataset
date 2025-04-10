<div align="center">

# OTTO Recommender Systems Dataset

[![GitHub stars](https://img.shields.io/github/stars/otto-de/recsys-dataset.svg?style=for-the-badge&color=yellow)](https://github.com/otto-de/recsys-dataset)
[![Test suite](https://img.shields.io/github/actions/workflow/status/otto-de/recsys-dataset/test.yml?branch=main&style=for-the-badge)](https://github.com/otto-de/recsys-dataset/actions/workflows/test.yml)
[![Kaggle competition](https://img.shields.io/badge/kaggle-competition-20BEFF?style=for-the-badge&logo=kaggle)](https://www.kaggle.com/competitions/otto-recommender-system)
[![OTTO jobs](https://img.shields.io/badge/otto-jobs-F00020?style=for-the-badge&logo=otto)](https://www.otto.de/jobs/technology/ueberblick/)

**A real-world e-commerce dataset for session-based recommender systems research.**

<img src=".readme/header.png" width="100%">

---
<p align="center">
  <a href="#get-the-data">Get the Data</a> •
  <a href="#data-format">Data Format</a> •
  <a href="#installation">Installation</a> •
  <a href="#evaluation">Evaluation</a> •
  <a href="#faq">FAQ</a> •
  <a href="#license">License</a>
</p>

</div>

The `OTTO` session dataset is a large-scale, industry-grade dataset designed to bridge the gap between academic research and real-world applications in session-based and sequential recommendation. It features anonymized behavior logs from the [OTTO](https://otto.de) webshop and app, supporting both multi-objective (predicting clicks, carts, and orders) and single-objective tasks. With ready-to-use formats, clear evaluation metrics, and a focus on realistic, scalable research, this dataset aims to drive innovation in the recommender systems community and has been featured in our own [Kaggle competition](https://www.kaggle.com/competitions/otto-recommender-system).

## Key Features

- 12M real-world anonymized user sessions
- 220M events, consiting of `clicks`, `carts` and `orders`
- 1.8M unique articles in the catalogue
- Ready to use data in `.jsonl` format
- Evaluation metrics for single and multi-objective tasks

## Dataset Statistics

| Dataset |  #sessions |    #items |     #events |     #clicks |     #carts |   #orders | Density [%] |
| :------ | ---------: | --------: | ----------: | ----------: | ---------: | --------: | ----------: |
| Train   | 12.899.779 | 1.855.603 | 216.716.096 | 194.720.954 | 16.896.191 | 5.098.951 |      0.0005 |
| Test    |  1.671.803 | 1.019.357 |  13.851.293 |  12.340.303 |  1.155.698 |   355.292 |      0.0005 |

|                           |  mean |   std |  min |  50% |  75% |  90% |  95% |  max |
| :------------------------ | ----: | ----: | ---: | ---: | ---: | ---: | ---: | ---: |
| Train #events per session | 16.80 | 33.58 |    2 |    6 |   15 |   39 |   68 |  500 |
| Test  #events per session |  8.29 | 13.74 |    2 |    4 |    8 |   18 |   28 |  498 |

<details>
    <summary><strong>#events per session histogram (90th percentile)</strong></summary>
    <img src=".readme/events_per_session_p90.svg" width="800px">
</details>

|                        |   mean |    std |  min |  50% |  75% |  90% |  95% |    max |
| :--------------------- | -----: | -----: | ---: | ---: | ---: | ---: | ---: | -----: |
| Train #events per item | 116.79 | 728.85 |    3 |   20 |   56 |  183 |  398 | 129004 |
| Test #events per item  |  13.59 |  70.48 |    1 |    3 |    9 |   24 |   46 |  17068 |

<details>
    <summary><strong>#events per item histogram (90th percentile)</strong></summary>
    <img src=".readme/events_per_item_p90.svg" width="800px">
</details>

## Get the Data

The data is stored on the [Kaggle](https://www.kaggle.com/competitions/otto-recommender-system/data) platform and can be downloaded using their API:

```Shell
kaggle datasets download -d otto/recsys-dataset
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

## Train/Test Split

To evaluate a model's ability to predict future behavior, as required for deployment in a real-world webshop, we use a time-based validation split. The training set includes user sessions from a 4-week period, while the test set contains sessions from the following week. To prevent information leakage, any training sessions overlapping with the test period were trimmed, ensuring a clear separation between past and future data. The diagram below illustrates this process:

<div align="center">
  <img src=".readme/train_test_split.png" width="100%">
</div>

## Evaluation Metrics

To ensure research relevance and industry applicability, we provide standardized evaluation protocols that closely correlate with real-world performance. For consistent and reliable benchmarking, we strongly recommend:

- **Using the provided train/test split** to ensure direct comparability with other research results, without leaving out any items or sessions in the evaluation
- Evaluating on the **entire test sequences** without truncation
- **Never use sampling** during evaluation, as this will lead to misleading results ([see details here](https://dl.acm.org/doi/10.1145/3394486.3403226))

### Single-Objective Evaluation

For click prediction tasks, we recommend using **Recall@20** (preferred) and **MRR@20**, which have demonstrated strong correlation with business impact metrics in our production systems, as validated in our [research paper](https://arxiv.org/abs/2307.14906).

| Model | Recall@20 | MRR@20 | Epochs/h |
|---------------|-------|--------|----------|
| [GRU4Rec⁺](https://arxiv.org/abs/1706.03847) | 0.443 | 0.205 | 0.019 |
| [SASRec](https://arxiv.org/abs/1808.09781) | 0.307 | 0.180 | **0.248** |
| [TRON](https://arxiv.org/abs/2307.14906) | **0.472** | **0.219** | 0.227 |

### Multi-Objective Evaluation

For models predicting multiple user actions, we offer two approaches:

1. **Joint Recall Metric**: Developed for our [Kaggle competition](https://www.kaggle.com/competitions/otto-recommender-system), this metric integrates recall scores for clicks, basket additions, and orders into a single comprehensive measure
2. **MultiTRON**: An approach that optimizes for clicks and orders simultaneously, allowing for evaluation of different preference trade-offs as detailed in our [research paper](https://arxiv.org/abs/2407.16828)

Note that multi-objective recommendation evaluation remains an active research area without definitive benchmarks. We welcome further research and contributions to improve evaluation methodologies for these complex scenarios.

## Kaggle Competition

For detailed usage instructions and evaluation guidelines regarding the competition, please refer to the [KAGGLE.md](KAGGLE.md) file.

## FAQ

### How is a user `session` defined?

- A session is all activity by a single user either in the train or the test set.

### Are there identical users in the train and test data?

- No, train and test users are completely disjunct.

### Are all test `aids` included in the train set?

- Yes, all test items are also included in the train set.

### How can a session start with an order or a cart?

- This can happen if the ordered item was already in the customer's cart before the data extraction period started. Similarly, a wishlist in our shop can lead to cart additions without a previous click.

### Are `aids` the same as article numbers on [otto.de](otto.de)?

- No, all article and session IDs are anonymized.

### Are most of the clicks generated by our current recommendations?

- No, our current recommendations generated only about 20% of the product page views in the dataset. Most users reached product pages via search results and product lists.

## License

The OTTO dataset is released under the [CC-BY 4.0 License](https://creativecommons.org/licenses/by/4.0/), while the code is licensed under the [MIT License](LICENSE).

## Citation

BibTeX entry:

```BibTeX
@online{philipp_normann_sophie_baumeister_timo_wilm_2023,
 title={OTTO Recommender Systems Dataset: A real-world e-commerce dataset for session-based recommender systems research},
 url={https://www.kaggle.com/dsv/4991874},
 doi={10.34740/KAGGLE/DSV/4991874},
 publisher={Kaggle},
 author={Philipp Normann and Sophie Baumeister and Timo Wilm},
 year={2023}
}
```
