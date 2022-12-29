import argparse

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import VarianceThreshold
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import Binarizer, StandardScaler
from sklearn.cross_decomposition import PLSRegression

def prepare_args():
    parser = argparse.ArgumentParser(
        prog="defect-model-builder",
        description="Build defect prediction models"
    )
    parser.add_argument("-d", "--defects", required=True, type=str)
    return parser.parse_args()

def load_defects_data(defects_file):
    return pd.read_csv(defects_file, sep=",").dropna()


def new_pipeline():
    return make_pipeline(
        PCA(),
        StandardScaler(),
        RandomForestClassifier(random_state=0)
    )

def run_ml_process(predictors, classes):
    pipeline = new_pipeline()

    predictors_train, predictors_test, classes_train, classes_test = train_test_split(predictors, classes, test_size=0.2, random_state=0, stratify=classes)

    pipeline.fit(predictors_train, classes_train)
    predictions = pipeline.predict(predictors_test)
    print(metrics.f1_score(classes_test, predictions))

def run_as_main():
    args = prepare_args()
    defects = load_defects_data(args.defects)
    predictors = ["la","ld","nf","nd","ns","ent","ndev","age","auc","aexpr","arexp","asexp"]
    run_ml_process(defects.filter(items=predictors), defects.filter(items=["buggy"]).values.ravel())
    print("Running for", args)

if __name__ == '__main__':
    run_as_main()
