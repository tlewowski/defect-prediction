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
    parser.add_argument("-r", "--reviews", required=True, type=str)
    parser.add_argument("-c", "--class-metrics", required=True, type=str)
    parser.add_argument("-i", "--include-smell", action="append", required=True, type=str)
    return parser.parse_args()


SEVERITIES = {
    'none': 0,
    'minor': 1,
    'major': 2,
    'critical': 3
}


def load_mlcq_samples(reviews_file):
    smell_reviews = pd.read_csv(reviews_file, sep=";").filter(items=["smell", "sample_id", "reviewer_id", "severity"])
    smell_reviews["severity"] = smell_reviews["severity"].transform(SEVERITIES.get)

    return smell_reviews

def load_class_metrics(metrics_file):
    metrics = pd.read_csv(metrics_file, sep=",", index_col="SampleId").dropna()
    metrics.drop(columns=["SampleType"], inplace=True)
    return metrics

def new_pipeline():
    return make_pipeline(
        PCA(),
        StandardScaler(),
        RandomForestClassifier(random_state=0)
    )
def run_ml_process(data):
    pipeline = new_pipeline()

    classes = data["severity"]
    independent_variables = data.drop(columns = ["severity"])

    predictors_train, predictors_test, classes_train, classes_test = train_test_split(independent_variables, classes, test_size=0.2, random_state=0, stratify=classes)

    pipeline.fit(predictors_train, classes_train)
    predictions = pipeline.predict(predictors_test)
    print(metrics.f1_score(classes_test, predictions))

def run_as_main():
    args = prepare_args()
    print("Running for", args.include_smell)
    class_metrics = load_class_metrics(args.class_metrics)
    reviews = load_mlcq_samples(args.reviews)

    for smell in args.include_smell:
        smell_reviews = reviews[reviews["smell"] == smell]
        class_data = smell_reviews.filter(["sample_id", "severity"]).groupby("sample_id")
        class_data = class_data.median().astype("int").transform(lambda c: c > 1.5)
        ml_input_data = class_data.join(class_metrics, how="inner")
        run_ml_process(ml_input_data)

if __name__ == '__main__':
    run_as_main()
