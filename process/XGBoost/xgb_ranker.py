import matplotlib.pyplot as plt
from merlin.core.utils import Distributed
from merlin.models.xgb import XGBoost
from merlin.schema.tags import Tags
from nvtabular import *
from nvtabular.ops import AddTags
import polars as pl
import xgboost as xgb

import helpers


def preprocess_data(df, transformations):
    """Apply a list of transformations to a DataFrame."""
    for transform in transformations:
        df = transform(df)
    return df


def load_and_preprocess_data(pipeline):
    """Load and preprocess train and label data."""
    train_data = pl.read_parquet('../../test/resources/test.parquet')
    train_labels = pl.read_parquet('../../test/resources/test_labels.parquet')
    train_data = preprocess_data(train_data, pipeline)

    return train_data, train_labels


def convert_labels(df):
    """Converts the labels to appropriate format."""
    id_by_type = {"clicks": 0, "carts": 1, "orders": 2}

    df = df.explode('ground_truth').with_columns([
        pl.col('ground_truth').alias('aid'),
        pl.col('type').apply(lambda x: id_by_type[x])
    ])[['session', 'type', 'aid']]

    df = df.with_columns([
        pl.col('session').cast(pl.datatypes.Int32),
        pl.col('type').cast(pl.datatypes.UInt8),
        pl.col('aid').cast(pl.datatypes.Int32)
    ])

    return df.with_columns(pl.lit(1).alias('gt'))


def build_model(train, labels):
    """Train the model on the given train data and labels."""
    train_labels = convert_labels(labels)

    train = train.join(train_labels, how='left', on=[
                       'session', 'type', 'aid']).with_columns(pl.col('gt').fill_null(0))

    data_set = Dataset(train.to_pandas())

    feature_cols = ['aid', 'type', 'session_duration', 'reversed_cumulative_count',
                    'session_recency_factor', 'weighted_session_recency_factor']
    target_col = ['gt'] >> AddTags([Tags.TARGET])
    id_col = ['session'] >> AddTags([Tags.USER_ID])

    wf = Workflow(feature_cols + target_col + id_col)
    train_processed = wf.fit_transform(data_set)

    # You can also modify the objective to use MAP or pairwise ranking instead
    ranker = XGBoost(train_processed.schema, objective='rank:ndcg')

    with Distributed():
        ranker.fit(train_processed)

    return ranker, wf


def plot_feature_importance(ranker):
    """Plot feature importance of the trained model."""
    ranker.booster.save_model('xgb_model.json')
    bst = xgb.Booster()
    bst.load_model('xgb_model.json')

    fig, ax = plt.subplots(figsize=(16, 8))
    xgb.plot_importance(bst, ax=ax)
    plt.tight_layout()
    plt.savefig('feature_importance.png')


def make_predictions(ranker, wf, pipeline):
    """Make predictions on test data and create a submission file."""
    test_data = pl.read_parquet('../../test/resources/test_full.parquet')
    test_data = preprocess_data(test_data, pipeline)
    data_set = Dataset(test_data.to_pandas())

    wf = wf.remove_inputs(['gt'])
    test_processed = wf.transform(data_set)

    test_preds = ranker.booster.predict(
        xgb.DMatrix(test_processed.compute()))

    test_data = test_data.with_columns(
        pl.Series(name='score', values=test_preds))

    test_predictions = test_data.sort(['session', 'score'], descending=True).groupby('session').agg([
        pl.col('aid').apply(list).alias('aid_list')
    ])

    test_predictions = test_predictions.with_columns(
        pl.col('aid_list').apply(lambda x: x[:20] if len(x) > 20 else x)
    )

    return test_predictions


def create_submission_file(test_predictions):
    """Create a submission file from the test predictions and sort."""
    session_types = []
    labels = []

    for session, preds in zip(test_predictions['session'].to_numpy(), test_predictions['aid_list'].to_numpy()):
        aid = ' '.join(str(pred) for pred in preds)
        for session_type in ['clicks', 'carts', 'orders']:
            labels.append(aid)
            session_types.append(f'{session}_{session_type}')

    submission = pl.DataFrame(
        {'session_type': session_types, 'labels': labels})

    submission = submission.with_columns([
        submission['session_type'].apply(lambda x: int(
            x.split('_')[0]), return_dtype=pl.Int64).alias('session_num'),
        submission['session_type'].apply(
            lambda x: x.split('_')[1]).alias('session_action')
    ])

    action_order = {'clicks': 0, 'carts': 1, 'orders': 2}

    submission = submission.with_columns([
        submission['session_action'].apply(
            lambda x: action_order[x]).alias('action_order')
    ])
    submission = submission.sort(['session_num', 'action_order'])
    submission = submission.drop(
        ['session_num', 'action_order', 'session_action'])

    submission.write_csv('predictions.csv')


def main():
    pipeline = helpers.get_pipeline()
    train_data, train_labels = load_and_preprocess_data(pipeline)
    ranker, workflow = build_model(train_data, train_labels)
    plot_feature_importance(ranker)
    predictions = make_predictions(ranker, workflow, pipeline)
    create_submission_file(predictions)


if __name__ == "__main__":
    main()
