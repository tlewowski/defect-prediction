import argparse
import datetime
import hashlib
import os
import sys
import time
from statistics import mean

import humanize
import numpy
import pandas as pd
import skops.io
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import *
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from utils import cleanse
from smell_schema import METRIC_SETS

def tp_scorer(clf, X, y):
    y_pred = clf.predict(X)
    cm = confusion_matrix(y, y_pred)
    return cm[1, 1]
def tn_scorer(clf, X, y):
    y_pred = clf.predict(X)
    cm = confusion_matrix(y, y_pred)
    return cm[0, 0]

def fp_scorer(clf, X, y):
    y_pred = clf.predict(X)
    cm = confusion_matrix(y, y_pred)
    return cm[0, 1]

def fn_scorer(clf, X, y):
    y_pred = clf.predict(X)
    cm = confusion_matrix(y, y_pred)
    return cm[1, 0]

def prepare_args(args):
    parser = argparse.ArgumentParser(
        prog="smell-model-builder",
        description="Build code smell models"
    )
    parser.add_argument("--data_file", required=True, type=str, help="data file to use for training")
    parser.add_argument("--smell", required=True, type=str, choices=["blob", "data class"], help="smell to be learned")
    parser.add_argument("--metric_set", required=True, type=str, help="which set of metrics shall be used for prediction", choices=METRIC_SETS.keys())
    parser.add_argument("--model_target", required=True, type=str, help="location where final model has to be put")
    parser.add_argument("--workspace", required=True, type=str, help="workspace location for temporary files")
    parser.add_argument("--random_seed", required=False, type=int, help="Random seed to use in the model building")
    parser.add_argument("--cv", required=False, type=int, help="Number of cross validation folds", default=10)
    return parser.parse_args(args)


SEVERITIES = {
    'none': 0,
    'minor': 1,
    'major': 2,
    'critical': 3
}

def new_pipeline(rng):
    return make_pipeline(
        PCA(),
        StandardScaler(),
        RandomForestClassifier(random_state=rng)
    )

def train_model(pipeline, predictors, classes):
    calculation_start_time = time.monotonic()
    print("SMELL_PIPELINE: Triggering training! Got", len(predictors), "entries for training and", len(classes), "entries for testing")
    pipeline.fit(predictors, classes)
    calculation_end_time = time.monotonic()
    print("SMELL_PIPELINE: Finished training in ",
          humanize.naturaldelta(datetime.timedelta(seconds=calculation_end_time-calculation_start_time), minimum_unit="milliseconds"))

    return pipeline


def run_ml_process(predictors, classes, rng, cv):
    pipeline = new_pipeline(rng)

    if cv == 0:
        return train_model(pipeline, predictors, classes), {}

    print("SMELL_PIPELINE: Triggering training with CV ({} folds)".format(cv))

    scoring = {
        "mcc": make_scorer(matthews_corrcoef),
        "accuracy": make_scorer(accuracy_score),
        "f1-score": make_scorer(f1_score),
        "precision": make_scorer(precision_score),
        "recall": make_scorer(recall_score),
        "balanced_accuracy": make_scorer(balanced_accuracy_score),
        "tp": tp_scorer,
        "tn": tn_scorer,
        "fp": fp_scorer,
        "fn": fn_scorer
    }


    calculation_start_time = time.monotonic()
    results = cross_validate(pipeline, predictors, classes, cv=cv, scoring=scoring)
    calculation_end_time = time.monotonic()

    print("SMELL_PIPELINE: Finished CV in ",
          humanize.naturaldelta(datetime.timedelta(seconds=calculation_end_time-calculation_start_time), minimum_unit="milliseconds"),
          ". Mean MCC: ", mean(results["test_mcc"]))

    return None, results


def select_relevant_rows_and_columns(data, metric_set, smell):
    all_cols = []
    all_cols.extend(METRIC_SETS[metric_set])
    all_cols.append("severity")
    all_cols.append("sample_id")

    cleansed_data = cleanse(data[data["smell"] == smell], all_cols, allow_drop=False)
    cleansed_data["severity"] = cleansed_data["severity"].transform(lambda x: SEVERITIES[x])

    aggregated_severity = cleansed_data.groupby("sample_id").median()

    print("SMELL_PIPELINE: After sample_based aggregation {} samples left".format(len(aggregated_severity.index)))

    predictors = aggregated_severity.loc[:, METRIC_SETS[metric_set]]
    predictions = aggregated_severity.loc[:, "severity"].transform(lambda x: x >= 1).values.ravel()

    return predictors, predictions

def run_with_args(args):
    args = prepare_args(args)

    with open(args.data_file, "rb") as f:
        datafile_checksum = hashlib.sha256(f.read()).hexdigest()

    data = pd.read_csv(args.data_file, sep=",")
    print("SMELL_PIPELINE: Loaded data. Got", len(data.index), "entries from", args.data_file)

    predictors, predictions = select_relevant_rows_and_columns(data, args.metric_set, args.smell)

    model, performance_metrics = run_ml_process(predictors, predictions, numpy.random.RandomState(args.random_seed), args.cv)
    output = {
        "model": model,
        "smell": args.smell,
        "metric_set": args.metric_set,
        "performance_metrics": performance_metrics,
        "name": "SMELL_" + os.path.basename(args.model_target),
        "seed": args.random_seed,
        "cv": args.cv,
        "data_file": args.data_file,
        "data_file_sha256_checksum": datafile_checksum
    }

    print("SMELL_PIPELINE: Saving built pipeline to {}".format(args.model_target))
    skops.io.dump(output, args.model_target)
    return output


def run_as_main():
    run_with_args(sys.argv[1:])


if __name__ == '__main__':
    run_as_main()
