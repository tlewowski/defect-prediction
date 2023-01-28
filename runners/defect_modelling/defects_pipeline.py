import argparse
import datetime
import functools
import os.path
import time

import numpy
import skops.io
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

from defect_schema import METRIC_SETS, CLASS_SETS
from smell_modelling.evaluate import evaluate_frame
from smell_modelling.utils import cleanse


def prepare_args():
    parser = argparse.ArgumentParser(
        prog="defect-model-builder",
        description="Build defect prediction models"
    )
    parser.add_argument("--input_data", required=True, help="file with defects, class and commit metrics", type=str)
    parser.add_argument("--metric_set", required=True, help="which set of metrics shall be used for prediction", choices=METRIC_SETS.keys())
    parser.add_argument("--class_set", required=True, help="which features shall be treated as the class columns", choices=CLASS_SETS.keys())
    parser.add_argument("--smell_models", required=False, help="paths to all code smell models that are supposed to be predictors", nargs="*", type=str)
    parser.add_argument("--random_seed", required=False, type=int, help="Random seed to use in the model building")

    return parser.parse_args()

def new_pipeline():
    return make_pipeline(
        PCA(),
        StandardScaler(),
        RidgeClassifier()
        #SVC()
        #RandomForestClassifier(random_state=0)
    )

def run_ml_process(predictors, classes, rng):
    pipeline = new_pipeline()
    predictors_train, predictors_test, classes_train, classes_test = train_test_split(predictors, classes, test_size=0.2, random_state=rng, stratify=classes)

    print("DEFECT_PIPELINE: Triggering training! Got", len(predictors_train), "entries for training and", len(classes_test), "entries for testing")

    calculation_start_time = time.monotonic()
    pipeline.fit(predictors_train, classes_train)
    calculation_end_time = time.monotonic()

    predictions = pipeline.predict(predictors_test)
    print("DEFECT_PIPELINE: Finished training in ",
          humanize.naturaldelta(datetime.timedelta(seconds=calculation_end_time-calculation_start_time), minimum_unit="milliseconds"),
          ". MCC: ", metrics.matthews_corrcoef(classes_test, predictions))


def load_input(input_file):
    return pd.read_csv(input_file, sep=",")


def select_relevant_rows_and_columns(data, metric_set, class_set):
    all_cols = []
    all_cols.extend(METRIC_SETS[metric_set])
    all_cols.extend(CLASS_SETS[class_set])
    all_cols.extend([smell for smell in data.columns.values.tolist() if smell.startswith("SMELL_")])

    # FIXME: what if there are is a missing metric for all entries for a given commit? Whole commit will be skipped now
    # also, remove non-unique entries, e.g. if only commit metrics are used
    # that's important, because otherwise it'll affect performance calculations
    data_with_metrics = cleanse(data, all_cols).drop_duplicates()

    predictors = data_with_metrics.loc[:, METRIC_SETS[metric_set]]
    predictions = data_with_metrics.loc[:, CLASS_SETS[class_set]].values.ravel()

    return predictors, predictions


def calculate_smells(data, smell_models):
    results = [evaluate_frame(data, skops.io.load(model, trusted=True)) for model in smell_models]
    return functools.reduce(lambda l, r: l.join(r, how="outer"), results).sort_index()


def run_as_main():
    args = prepare_args()
    input_file = os.path.abspath(args.input_data)
    data = load_input(input_file)
    print("DEFECT_PIPELINE: Loaded data. Got", len(data.index), "entries from", input_file)

    if args.smell_models:
        smell_predictors = calculate_smells(data, args.smell_models)
        print("DEFECT_PIPELINE: Adding data from {} smell models: {}".format(len(args.smell_models), smell_predictors.columns.values.tolist()))
        data = data.join(smell_predictors)

    predictors, predictions = select_relevant_rows_and_columns(data, args.metric_set, args.class_set)
    print("DEFECT_PIPELINE: Using", args.metric_set, "as metrics and", args.class_set, "as classes. Got", len(predictions), "entries")
    run_ml_process(predictors, predictions, numpy.random.RandomState(args.random_seed))


if __name__ == '__main__':
    run_as_main()

#%%
