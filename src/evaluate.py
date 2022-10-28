import argparse
import json
from pathlib import Path

from beartype import beartype


@beartype
def prepare_predictions(predictions: list[str]):
    prepared_predictions = dict()
    for prediction in predictions:
        sid_type, preds = prediction.strip().split(",")
        sid, event_type = sid_type.split("_")
        preds = [int(aid) for aid in preds.split(" ")] if preds != "" else []
        if not int(sid) in prepared_predictions:
            prepared_predictions[int(sid)] = dict()
        prepared_predictions[int(sid)][event_type] = preds
    return prepared_predictions


@beartype
def prepare_labels(labels: list[dict]):
    final_labels = dict()
    for label in labels:
        final_labels[label["session"]] = {
            "clicks": label["labels"].get("clicks", None),
            "carts": set(label["labels"].get("carts", [])),
            "orders": set(label["labels"].get("orders", []))
        }
    return final_labels


@beartype
def evaluate_session(labels: dict, prediction: dict, k: int):
    if 'clicks' in labels and labels['clicks']:
        clicks_hit = float(labels['clicks'] in prediction['clicks'][:k])
    else:
        clicks_hit = None

    if 'carts' in labels and labels['carts']:
        cart_hits = len(set(prediction['carts'][:k]).intersection(labels['carts']))
    else:
        cart_hits = None

    if 'orders' in labels and labels['orders']:
        order_hits = len(set(prediction['orders'][:k]).intersection(labels['orders']))
    else:
        order_hits = None

    return {'clicks': clicks_hit, 'carts': cart_hits, 'orders': order_hits}


@beartype
def evaluate_sessions(labels: dict[str, dict], predictions: dict[int, dict], k: int):
    result = {}
    for session_id, session_labels in labels.items():
        if session_id in predictions:
            result[session_id] = evaluate_session(session_labels, predictions[session_id], k)
        else:
            result[session_id] = {k: 0. if v else None for k, v in session_labels.items()}
    return result


@beartype
def num_events(labels: dict[int, dict], k: int):
    num_clicks = 0
    num_carts = 0
    num_orders = 0
    for event in labels.values():
        if 'clicks' in event and event['clicks']:
            num_clicks += 1
        if 'carts' in event and event['carts']:
            num_carts += min(len(event["carts"]), k)
        if 'orders' in event and event['orders']:
            num_orders += min(len(event["orders"]), k)
    return {'clicks': num_clicks, 'carts': num_carts, 'orders': num_orders}


@beartype
def recall_by_event_type(evalutated_events: dict, total_number_events: dict):
    clicks = 0
    carts = 0
    orders = 0
    for event in evalutated_events.values():
        if 'clicks' in event and event['clicks']:
            clicks += event['clicks']
        if 'carts' in event and event['carts']:
            carts += event['carts']
        if 'orders' in event and event['orders']:
            orders += event['orders']

    return {
        'clicks': clicks / total_number_events['clicks'],
        'carts': carts / total_number_events['carts'],
        'orders': orders / total_number_events['orders']
    }


@beartype
def weighted_recalls(recalls: dict, weights: dict):
    result = 0.0
    for event, recall in recalls.items():
        result += recall * weights[event]
    return result


@beartype
def get_scores(labels: dict[int, dict],
               predictions: dict[int, dict],
               k=20,
               weights={
                   'clicks': 0.10,
                   'carts': 0.30,
                   'orders': 0.60
               }):
    '''
    Calculates the weighted recall for the given predictions and labels.
    Args:
        labels: dict of labels for each session
        predictions: dict of predictions for each session
        k: cutoff for the recall calculation
        weights: weights for the different event types
    Returns:
        recalls for each event type and the weighted recall
    '''
    total_number_events = num_events(labels, k)
    evaluated_events = evaluate_sessions(labels, predictions, k)
    recalls = recall_by_event_type(evaluated_events, total_number_events)
    recalls["total"] = weighted_recalls(recalls, weights)
    return recalls


@beartype
def main(labels_path: Path, predictions_path: Path):
    with open(labels_path, "r") as f:
        labels = prepare_labels([json.loads(label) for label in f.readlines()])
    with open(predictions_path, "r") as f:
        predictions = prepare_predictions(f.readlines()[1:])
    print(get_scores(labels, predictions))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-labels', default="resources/test_labels.jsonl", type=str)
    parser.add_argument('--predictions', default="resources/predictions.csv", type=str)
    args = parser.parse_args()
    main(Path(args.test_labels), Path(args.predictions))
