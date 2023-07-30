# Asha Raghav
# z5363204
# COMP9417 Group Project
# Word2Vec model
# Authored 27/07/23

# TODO: Download the train and test parquet files from:
# https://www.kaggle.com/datasets/columbia2131/otto-chunk-data-inparquet-format?select=test_parquet
# Save the parquet folders (test_parquet, train_parquet) to the test/resources/ directory.

from annoy import AnnoyIndex
import numpy as np
import glob
import pandas as pd
from collections import defaultdict
import polars as pl
import os
from gensim.models import Word2Vec
import pandas as pd
import pickle


def load_data(pickle_file, data_file):
    '''
        Retrieves data from a given file using cache.

        If the pickle file exists with the data, retrieves it from the file.
        Otherwise, as retrieving data from a file for the first time,
        stores in a pickle file for faster future retrieval.

        Params:
            pickle_file (str): file path of pickle file containing required data
            data_file (str): file path of file containing data to be stored and used

        Returns: 
            DataFrame of polars type
    '''

    if os.path.exists(pickle_file):
        print('Reading data from cache')
        return pickle.load(open(pickle_file, 'rb'))
    else:
        # No cache, so make file and save for subsequent runs
        with open(pickle_file, 'wb') as f:
            files = sorted(glob.glob(data_file))
            dfs = []
            for fpath in files:
                dfs.append(pd.read_parquet(fpath))
            dfs = pl.DataFrame(pd.concat(dfs).reset_index(drop=True))
            pickle.dump(dfs, f)
        return dfs


def transform_data(train_data, test_data):
    '''
        Changes data to a form that the gensim model can iterate with.

        Uses polars to merge datasets to train on.

        Params:
            train_data (polars df): dataframe with the training data
            test_data (polars df): dataframe with the test data

        Returns:
            Dataframe with iterable session values
    '''

    # Merge data into one dataframe
    transformed_df = pl.concat([train_data, test_data]).groupby(
        'session').agg(pl.col('aid').alias('s'))
    return transformed_df['s'].to_list()


def generate_labels(test_sts, test_sAIDs):
    '''
        Creates predictions using word2Vec embeddings and approximate nearest neighbour search.

        Generates up to 20 AID values and sorts them based on event type weightage given. 

        Params:
            test_sts (list): list grouped by the test session types 
            test_sAIDs (list): list grouped by the test session Article ID (AID) values

        Returns:
            labs (list): generated list of up to 20 AID values for each session id and type in the test set
    '''

    # Stores label values
    labs = []
    # Weights obtained from covisitation matrix corresponding to clicks, carts, orders
    type_weight = {0: 1, 1: 6, 2: 3}
    for AIDs, event_types in zip(test_sAIDs, test_sts):
        if len(AIDs) >= 20:
            # If no need to generate more candidates (already having 20)
            weights = np.logspace(0.1, 1, len(AIDs), base=2, endpoint=True) - 1
            # Make a copy of the AIDs with key value pairs corresponding to the weights we will give
            aids_copy = defaultdict(lambda: 0)
            # Iterate through and apply weights
            for aid, w, t in zip(AIDs, weights, event_types):
                # Assign the event types to corresponding indices
                type_dict = {'clicks': 0, 'carts': 1, 'orders': 2}
                # Calculate weighting to assigned AID value
                aids_copy[aid] += w * type_weight[type_dict[t]]
            # Sort article ID values corresponding to the given weightings in the items
            sorted_aid_vals = [k for k, v in sorted(
                aids_copy.items(), key=lambda item: -item[1])]
            # Store the ordered predictions
            labs.append(sorted_aid_vals[:20])
        else:
            # Utilise word2vec embeddings in candidate generation
            AIDs = list(dict.fromkeys(AIDs[::-1]))
            # Search for the nearest aid values to the current AID value
            nearest_neighbours = [w2v_model.wv.index_to_key[i]
                                  for i in index.get_nns_by_item(aid_index[AIDs[0]], 21)[1:]]
            # Add the nearest neighbours to the AID value predictions
            labs.append((AIDs+nearest_neighbours)[:20])
    # Join all the prediction values, space separated
    labs = [' '.join([str(lab) for lab in labels]) for labels in labs]
    return labs


def format_predictions(test_sAIDs, labels):
    '''
        Formats the predictions as required in submission.csv.

        Ensures sessiontype and session id are combined to form rows with their corresponding predicted AID values.

        Params:
            test_sAIDs (Pandas dataframe): contains the test session ids
            labels (list): contains the predicted session AID values

        Returns:
            Pandas dataframe: containing predicted AID values for each session (labels)
    '''
    w2v_predictions = pd.DataFrame(data={'session_type': test_sAIDs.index,
                                   'labels': labels})
    prediction_dfs = []
    session_type = ['clicks', 'carts', 'orders']
    for st in session_type:
        # Reformat as submission code
        formatted_predictions = w2v_predictions.copy()
        formatted_predictions.session_type = formatted_predictions.session_type.astype(
            'str') + f'_{st}'
        prediction_dfs.append(formatted_predictions)

    return pd.concat(prediction_dfs).reset_index(drop=True)


def main():
    # Load in the data from the parquet files (assuming they are located in the test/resources/ directory)
    train = load_data('../../test/resources/all_train_data.pkl',
                      '../../test/resources/train_parquet/*')
    test = load_data('../../test/resources/all_test_data.pkl',
                     '../../test/resources/test_parquet/*')

    # Train word2vec model
    w2v_model = Word2Vec(sentences=transform_data(
        train, test), vector_size=32, min_count=1, workers=4)

    # For Approx Nearest Neighbour search - create embeddings
    aid_index = {aid: i for i, aid in enumerate(w2v_model.wv.index_to_key)}
    index = AnnoyIndex(32, 'euclidean')
    for _, idx in aid_index.items():
        # Obtain embedding for a specific aid value
        index.add_item(idx, w2v_model.wv.vectors[idx])
    index.build(10)

    # Read in the sample submission file
    pd.read_csv('../../test/resources/sample_submission.csv')

    # Convert test session types and AIDs to lists
    test_sts = test.to_pandas().reset_index(
        drop=True).groupby('session')['type'].apply(list)
    test_sAIDs = test.to_pandas().reset_index(
        drop=True).groupby('session')['aid'].apply(list)

    # Create predictions using word2vec embeddings
    labels = generate_labels(test_sts, test_sAIDs)

    # Reformat the final dataframe
    final_preds = format_predictions(test_sAIDs, labels)

    # Save generated predictions to csv files
    final_preds.to_csv('predictions.csv', index=False)


if __name__ == '__main__':
    main()
