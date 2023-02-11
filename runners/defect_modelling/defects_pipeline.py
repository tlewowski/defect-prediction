import argparse
import datetime
import functools
import hashlib
import os.path
import sys
import time

import skops.io
import humanize
import pandas as pd
from shortuuid import random
from sklearn.linear_model import RidgeClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, \
    balanced_accuracy_score, matthews_corrcoef, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from defect_schema import METRIC_SETS, CLASS_SETS
from smell_modelling.evaluate import evaluate_frame
from utils import cleanse

def prepare_args(cmd_args):
    parser = argparse.ArgumentParser(
        prog="defect-model-builder",
        description="Build defect prediction models"
    )
    parser.add_argument("--input_data", required=True, help="file with defects, class and commit metrics", type=str)
    parser.add_argument("--metric_set", required=True, help="which set of metrics shall be used for prediction", choices=METRIC_SETS.keys())
    parser.add_argument("--class_set", required=True, help="which features shall be treated as the class columns", choices=CLASS_SETS.keys())
    parser.add_argument("--smell_models", required=False, help="paths to all code smell models that are supposed to be predictors", nargs="*", type=str)
    parser.add_argument("--random_seed", required=False, type=int, help="random seed to use in the model building")
    parser.add_argument("--training_fraction", required=False, type=float, help="fraction of data set to be used in training", default=0.8)
    parser.add_argument("--model_target", required=False, type=str, help="location where model will be saved")

    return parser.parse_args(cmd_args)

def new_pipeline():
    return make_pipeline(
        PCA(),
        StandardScaler(),
        RidgeClassifier()
    )

def run_ml_process(predictors, classes, rng):
    pipeline = new_pipeline()

    print("DEFECT_PIPELINE: Triggering training! Got", len(predictors), "entries for training and", len(classes), "entries for testing")

    calculation_start_time = time.monotonic()
    pipeline.fit(predictors, classes)
    calculation_end_time = time.monotonic()

    print("DEFECT_PIPELINE: Finished training in ", humanize.naturaldelta(datetime.timedelta(seconds=calculation_end_time-calculation_start_time), minimum_unit="milliseconds"))
    return pipeline

def test_ml_pipeline(pipeline, test_data, metric_set, class_set):
    revisions = test_data.loc[:, ["revision"]]
    test_predictors = test_data.loc[:, metric_set]
    classes = test_data.loc[:, class_set]
    predictions = pipeline.predict(test_predictors)

    scoring = {
        "mcc": matthews_corrcoef,
        "accuracy": accuracy_score,
        "f1-score": f1_score,
        "precision": precision_score,
        "recall": recall_score,
        "balanced_accuracy": balanced_accuracy_score,
        "tp": lambda actual,predicted: confusion_matrix(actual, predicted)[1,1],
        "tn": lambda actual,predicted: confusion_matrix(actual, predicted)[0,0],
        "fp": lambda actual,predicted: confusion_matrix(actual, predicted)[0,1],
        "fn": lambda actual,predicted: confusion_matrix(actual, predicted)[1,0]
    }

    fake_scores = dict([(metric, scoring[metric](classes, predictions)) for metric in scoring.keys()])

    print("Fake scores", fake_scores)

    per_commit_predictions = revisions.join(pd.DataFrame(predictions, index=revisions.index)).groupby(["revision"]).any()
    per_commit_classes = revisions.join(classes).groupby(["revision"]).any()

    real_scores = dict([(metric, scoring[metric](per_commit_classes, per_commit_predictions)) for metric in scoring.keys()])

    print("Real scores", real_scores)

    return {
        "real": real_scores,
        "fake": fake_scores
    }




def load_input(input_file):
    data = pd.read_csv(input_file, sep=",")

    # Removing, because entries for Hadoop are broken
    return data[data["project"] != "hadoop"]

def select_relevant_columns(data, metric_set, class_set):
    all_cols = []
    all_cols.extend(metric_set)
    all_cols.extend(class_set)
    all_cols.append("revision")

    return cleanse(data, all_cols).drop_duplicates()


def calculate_smells(data, smell_models):
    results = [evaluate_frame(data, skops.io.load(model, trusted=True)) for model in smell_models]
    return functools.reduce(lambda l, r: l.join(r, how="outer"), results).sort_index()


def train_test_commit_split(data, class_set, train_ratio, random_state):
    cols = ["revision"]
    cols.extend(class_set)
    revision_data = data.loc[:, cols].drop_duplicates()

    train_revisions = revision_data.groupby(class_set).sample(frac=train_ratio, random_state=random_state)
    test_revisions = pd.concat([revision_data, train_revisions]).drop_duplicates(keep=False)
    print("DEFECT_PIPELINE: After split got", len(train_revisions.index), "samples for training and", len(test_revisions.index), "samples for training")
    return train_revisions, test_revisions


def run_with_args(cmd_args):
    preparation_start_ts = time.monotonic()
    args = prepare_args(cmd_args)
    input_file = os.path.abspath(args.input_data)
    data = load_input(input_file)

    if args.random_seed is not None:
        random.seed(args.random_seed)

    with open(args.data_file, "rb") as f:
        datafile_checksum = hashlib.sha256(f.read()).hexdigest()

    print("DEFECT_PIPELINE: Loaded data. Got", len(data.index), "entries from", input_file)

    metric_set = METRIC_SETS[args.metric_set].copy()
    class_set = CLASS_SETS[args.class_set].copy()

    if args.smell_models:
        smell_predictors = calculate_smells(data, args.smell_models)
        print("DEFECT_PIPELINE: Adding data from {} smell models: {}".format(len(args.smell_models), smell_predictors.columns.values.tolist()))
        data = data.join(smell_predictors)

    metric_set.extend([col for col in data.columns.values.ravel() if col.startswith("SMELL_")])

    relevant_data = select_relevant_columns(data, metric_set, class_set)

    training_revisions, testing_revisions = train_test_commit_split(data, class_set, args.training_fraction, random.randint(0, 2**32 - 1))
    training_data = relevant_data[relevant_data.revision.isin(training_revisions.revision)]
    testing_data = relevant_data[relevant_data.revision.isin(testing_revisions.revision)]

    fitting_start_ts = time.monotonic()
    print("DEFECT_PIPELINE: ML pipeline will be triggered with {} samples from {} revisions for training. Using predictor columns: {} for predicting {}"
          .format(len(training_data.index), len(training_revisions.index), metric_set, class_set))
    pipeline = run_ml_process(training_data.loc[:, metric_set], training_data.loc[:, class_set].values.ravel(), random.randint(0, 2**32 - 1))

    print("DEFECT_PIPELINE: Testing will be executed with {} samples from {} revisions".format(len(testing_data.index), len(testing_revisions.index)))

    testing_start_ts = time.monotonic()
    scores = test_ml_pipeline(pipeline, testing_data, metric_set, class_set)

    process_end_ts = time.monotonic()

    output = {
        "scores": scores,
        "model": pipeline,
        "metric_set": args.metric_set,
        "class_set": args.class_set,
        "name": "DEFECTS_" + os.path.basename(args.model_target or "UNNAMED"),
        "training_fraction": args.training_fraction,
        "data_file": args.data_file,
        "data_file_sha256_checksum": datafile_checksum,
        "smell_models": args.smell_models,
        "fit_time_ms": testing_start_ts - fitting_start_ts,
        "preparation_time_ms": fitting_start_ts - preparation_start_ts,
        "test_time_ms": process_end_ts - testing_start_ts
    }

    if args.model_target is not None:
        skops.io.dump(output, os.path.abspath(args.model_target))

    return output


def run_as_main():
    run_with_args(sys.argv[1:])


if __name__ == '__main__':
    run_as_main()
