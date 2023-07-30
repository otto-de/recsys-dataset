import polars as pl


def append_reversed_cumulative_count(df):
    return df.with_columns(
        pl.col('session').cumcount().reverse().over('session').alias('reversed_cumulative_count'))


def append_session_duration(df):
    return df.with_columns(pl.col('session').count().over('session').alias('session_duration'))


def append_session_recency_factor(df):
    interpolated_linearly = 0.1 + (0.9 / (df['session_duration'] - 1)) * (
        df['session_duration'] - df['reversed_cumulative_count'] - 1)
    return df.with_columns(pl.Series(2**interpolated_linearly - 1).alias('session_recency_factor')).fill_nan(1)


def append_weighted_session_recency_factor(df):
    type_weights = {0: 1, 1: 6, 2: 3}
    weighted_score = pl.Series(df['type'].apply(
        lambda x: type_weights[x]) * df['session_recency_factor'])
    return df.with_columns(weighted_score.alias('weighted_session_recency_factor'))


def get_pipeline():
    return [append_reversed_cumulative_count, append_session_duration,
            append_session_recency_factor, append_weighted_session_recency_factor]
