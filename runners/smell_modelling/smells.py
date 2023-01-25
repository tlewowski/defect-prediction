import argparse
import datetime
import hashlib
import os
import sys
import time

import humanize
import numpy
import pandas as pd
import skops.io
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from utils import cleanse
from smell_schema import METRIC_SETS

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
    parser.add_argument("--test_size", required=False, type=float, help="Fraction of the whole data set to be used as test set", default=0.2)
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
def run_ml_process(predictors, classes, rng, test_size):
    pipeline = new_pipeline(rng)

    if test_size > 0:
        predictors_train, predictors_test, classes_train, classes_test = train_test_split(predictors, classes, test_size=test_size, random_state=rng, stratify=classes)
    else:
        predictors_train = predictors
        classes_train = classes
        classes_test = []
        predictors_test = []

    print("SMELL_PIPELINE: Triggering training! Got", len(predictors_train), "entries for training and", len(classes_test), "entries for testing")

    calculation_start_time = time.monotonic()
    pipeline.fit(predictors_train, classes_train)
    calculation_end_time = time.monotonic()

    performance_metrics = {}
    if len(classes_test) > 0:
        predictions = pipeline.predict(predictors_test)
        if os.environ.get("SMELLS_PRINT_ALL_PREDICTIONS"):
            for i in range(len(predictions)):
                print("{}/{} -> {},".format("Y" if predictions[i] else "N", "Y" if classes_test[i] else "N", predictions[i] == classes_test[i]))

        print("SMELL_PIPELINE: Finished training in ",
              humanize.naturaldelta(datetime.timedelta(seconds=calculation_end_time-calculation_start_time), minimum_unit="milliseconds"),
              ". MCC: ", metrics.matthews_corrcoef(classes_test, predictions))

        performance_metrics = {
            "confusion_matrix": metrics.confusion_matrix(classes_test, predictions),
            "mcc": metrics.matthews_corrcoef(classes_test, predictions),
            "f1-score": metrics.f1_score(classes_test, predictions),
            "precision": metrics.precision_score(classes_test, predictions),
            "recall": metrics.recall_score(classes_test, predictions),
            "accuracy": metrics.accuracy_score(classes_test, predictions),
            "balanced_accuracy": metrics.balanced_accuracy_score(classes_test, predictions),
            "predictions": predictions
        }

    return pipeline, performance_metrics


def select_relevant_rows_and_columns(data, metric_set, smell):
    all_cols = []
    all_cols.extend(METRIC_SETS[metric_set])
    all_cols.append("severity")
    all_cols.append("sample_id")

    cleansed_data = cleanse(data[data["smell"] == smell], all_cols)
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

    model, performance_metrics = run_ml_process(predictors, predictions, numpy.random.RandomState(args.random_seed), args.test_size)
    output = {
        "model": model,
        "smell": args.smell,
        "metric_set": args.metric_set,
        "performance_metrics": performance_metrics,
        "name": "SMELL_" + os.path.basename(args.model_target),
        "seed": args.random_seed,
        "test_size": args.test_size,
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
