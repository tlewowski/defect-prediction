import argparse
import datetime
import functools
import os.path
import time

import humanize
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.linear_model import RidgeClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import VarianceThreshold
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import Binarizer, StandardScaler
from sklearn.cross_decomposition import PLSRegression
from sklearn.svm import SVC

from schema import METRIC_SETS, CLASS_SETS


def prepare_args():
    parser = argparse.ArgumentParser(
        prog="defect-model-builder",
        description="Build defect prediction models"
    )
    parser.add_argument("--input_data", required=True, help="file with defects, class and commit metrics", type=str)
    parser.add_argument("--metric_set", required=True, help="which set of metrics shall be used for prediction", choices=METRIC_SETS.keys())
    parser.add_argument("--class_set", required=True, help="which features shall be treated as the class columns", choices=CLASS_SETS.keys())

    return parser.parse_args()

def new_pipeline():
    return make_pipeline(
        PCA(),
        StandardScaler(),
        RidgeClassifier()
        #SVC()
        #RandomForestClassifier(random_state=0)
    )

def run_ml_process(predictors, classes):
    pipeline = new_pipeline()
    predictors_train, predictors_test, classes_train, classes_test = train_test_split(predictors, classes, test_size=0.2, random_state=0, stratify=classes)

    print("DEFECT_PIPELINE: Triggering training! Got", len(predictors_train), "entries for training and", len(classes_test), "entries for testing")

    calculation_start_time = time.monotonic()
    pipeline.fit(predictors_train, classes_train)
    calculation_end_time = time.monotonic()

    predictions = pipeline.predict(predictors_test)
    print("DEFECT_PIPELINE: Finished training in ",
          humanize.naturaldelta(datetime.timedelta(seconds=calculation_end_time-calculation_start_time), minimum_unit="milliseconds"),
          ". F-score: ", metrics.f1_score(classes_test, predictions))


def load_input(input_file):
    return pd.read_csv(input_file, sep=",")


def select_relevant_rows_and_columns(data, metric_set, class_set):
    all_cols = []
    all_cols.extend(METRIC_SETS[metric_set])
    all_cols.extend(CLASS_SETS[class_set])

    # FIXME: what if there are is a missing metric for all entries for a given commit? Whole commit will be skipped now
    # also, remove non-unique entries, e.g. if only commit metrics are used
    # that's important, because otherwise it'll affect performance calculations
    data_with_metrics = data.loc[:, all_cols].dropna().drop_duplicates()

    predictors = data_with_metrics.loc[:, METRIC_SETS[metric_set]]
    predictions = data_with_metrics.loc[:, CLASS_SETS[class_set]].values.ravel()

    return predictors, predictions

def run_as_main():
    args = prepare_args()
    input_file = os.path.abspath(args.input_data)
    data = load_input(input_file)
    print("DEFECT_PIPELINE: Loaded data. Got", len(data.index), "entries from", input_file)

    predictors, predictions = select_relevant_rows_and_columns(data, args.metric_set, args.class_set)
    print("DEFECT_PIPELINE: Using", args.metric_set, "as metrics and", args.class_set, "as classes. Got", len(predictions), "entries")
    run_ml_process(predictors, predictions)

if __name__ == '__main__':
    run_as_main()

#%%
