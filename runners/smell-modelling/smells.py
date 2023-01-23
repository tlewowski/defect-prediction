import argparse
import datetime
import os
import time

import humanize
import numpy
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.linear_model import RidgeClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import Binarizer, StandardScaler
from sklearn.cross_decomposition import PLSRegression

from schema import METRIC_SETS

class PLSPreProc(PLSRegression):
    ''' Wrapper to allow PLSRegression to be used in the Pipeline Module '''
    def __init__(self, n_components=2, scale=False, max_iter=1000, tol=1e-6, copy=True):
        super().__init__(n_components=n_components, scale=scale, max_iter=max_iter, tol=tol, copy=copy)

    def fit(self, X, y):
        return super().fit(X, y)

    def transform(self, X):
        return super().transform(X)

    def fit_transform(self, X, y):
        return self.fit(X,y).transform(X)

def prepare_args():
    parser = argparse.ArgumentParser(
        prog="smell-model-builder",
        description="Build code smell models"
    )
    parser.add_argument("--data_file", required=True, type=str)
    parser.add_argument("--smell", required=True, type=str, choices=["blob", "data class"])
    parser.add_argument("--metric_set", required=True, type=str, help="which set of metrics shall be used for prediction", choices=METRIC_SETS.keys())
    parser.add_argument("--model_target", required=True, type=str, help="location where final model has to be put")
    parser.add_argument("--workspace", required=True, type=str, help="workspace location for temporary files")
    parser.add_argument("--random_seed", required=False, type=int, help="Random seed to use in the model building")
    return parser.parse_args()


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
def run_ml_process(predictors, classes, rng):
    pipeline = new_pipeline(rng)
    predictors_train, predictors_test, classes_train, classes_test = train_test_split(predictors, classes, test_size=0.1, random_state=rng, stratify=classes)

    print("SMELL_PIPELINE: Triggering training! Got", len(predictors_train), "entries for training and", len(classes_test), "entries for testing")

    calculation_start_time = time.monotonic()
    pipeline.fit(predictors_train, classes_train)
    calculation_end_time = time.monotonic()

    predictions = pipeline.predict(predictors_test)
    if os.environ.get("SMELLS_PRINT_ALL_PREDICTIONS"):
        for i in range(len(predictions)):
            print("{}/{} -> {},".format("Y" if predictions[i] else "N", "Y" if classes_test[i] else "N", predictions[i] == classes_test[i]))


    print("SMELL_PIPELINE: Finished training in ",
          humanize.naturaldelta(datetime.timedelta(seconds=calculation_end_time-calculation_start_time), minimum_unit="milliseconds"),
          ". MCC: ", metrics.matthews_corrcoef(classes_test, predictions))


def cleanse(data, smell, all_cols):
    relevant_data = data[data["smell"] == smell].loc[:, all_cols]

    print("SMELL_PIPELINE: Total of {} reviews for {}".format(len(relevant_data.index), smell))

    if "PMD_TCC" in relevant_data:
        # filling in for utility classes, that have no members
        relevant_data["PMD_TCC"].fillna(2, inplace=True)
    if "PMD_WOC" in relevant_data:
        # filling in for utility classes that have no non-static methods
        relevant_data["PMD_WOC"].fillna(2, inplace=True)

#    relevant_data.fillna(5000, inplace=True)

    dropped = relevant_data.dropna()
    print("SMELL_PIPELINE: After dropping NAs, {} reviews left (up for grouping)".format(len(dropped.index)))
    return dropped

def select_relevant_rows_and_columns(data, metric_set, smell):
    all_cols = []
    all_cols.extend(METRIC_SETS[metric_set])
    all_cols.append("severity")
    all_cols.append("sample_id")

    cleansed_data = cleanse(data, smell, all_cols)
    cleansed_data["severity"] = cleansed_data["severity"].transform(lambda x: SEVERITIES[x])

    aggregated_severity = cleansed_data.groupby("sample_id").median()

    predictors = aggregated_severity.loc[:, METRIC_SETS[metric_set]]
    predictions = aggregated_severity.loc[:, "severity"].transform(lambda x: x >= 1).values.ravel()

    return predictors, predictions


def run_as_main():
    args = prepare_args()
    data = pd.read_csv(args.data_file, sep=",")
    print("SMELL_PIPELINE: Loaded data. Got", len(data.index), "entries from", args.data_file)

    predictors, predictions = select_relevant_rows_and_columns(data, args.metric_set, args.smell)

    run_ml_process(predictors, predictions, numpy.random.RandomState(args.random_seed))


if __name__ == '__main__':
    run_as_main()
