import csv
import os
import numpy
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.base import BaseEstimator
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.feature_selection import SelectFromModel, SelectKBest, chi2, RFECV
from sklearn.linear_model import RidgeClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier, XGBModel


# Inspired by https://stackoverflow.com/a/76310589

class WrappedFeatureSelection(BaseEstimator):
    def __init__(self, intermediate_model, artifacts_path):                # Pass through the estimator here
        self.intermediate_model = intermediate_model
        self.artifacts_path = artifacts_path

    def fit(self, X, y=None):                        # Assume model has already been fit
        return self.intermediate_model.fit(X, y)                                  # so do nothing here

    def transform(self, X):
        if self.artifacts_path is not None:
            line = [os.path.basename(self.artifacts_path)]
            used_features = self.intermediate_model.get_feature_names_out()
            line.extend(used_features)
            features_file = os.path.join(self.artifacts_path, "selected_features.csv")
            print("Used features: {}. Saving to {}".format(str(used_features), features_file))
            with open(features_file, 'w') as f:
                csv.writer(f).writerow(line)

        return self.intermediate_model.transform(X)    # alias predict as transform


def scaled_linear_ridge_pipeline():
    return make_pipeline(
        PCA(),
        StandardScaler(),
        RidgeClassifier()
    )


def unscaled_linear_ridge_pipeline():
    return make_pipeline(RidgeClassifier())


def scaled_randomforest_pipeline(rng):
    return make_pipeline(
        PCA(),
        StandardScaler(),
        RandomForestClassifier(random_state=rng)
    )


def unscaled_randomforest_pipeline(rng):
    return make_pipeline(RandomForestClassifier(random_state=rng))


def unscaled_decisiontree_pipeline():
    return make_pipeline(DecisionTreeClassifier())


def unscaled_catboost_pipeline_creator(false_weight):
    return lambda rng: make_pipeline(
        CatBoostClassifier(
            class_weights={
                1: 1-false_weight,
                0: false_weight
            },
            random_state=rng
        )
    )


def unscaled_lgbm_pipeline (rng):
    return make_pipeline(LGBMClassifier(random_state=rng))


def unscaled_xgboost_pipeline(rng):
    return make_pipeline(XGBClassifier(XGBModel(random_state=rng)))


def scaled_adaboost_pipeline(rng):
    return make_pipeline(
        PCA(),
        StandardScaler(),
        AdaBoostClassifier(random_state=rng)
    )


def scaled_gradientboost_pipeline(rng):
    return make_pipeline(
        PCA(),
        StandardScaler(),
        GradientBoostingClassifier(random_state=rng)
    )

def unscaled_featureselected_n_svc_randomforest_pipeline(n):
    def f(rng, artifacts_path):
        return make_pipeline(
            WrappedFeatureSelection(
                SelectFromModel(
                    LinearSVC(penalty="l2", max_iter=2500, random_state=rng),
                    max_features=n
                ),
                artifacts_path
            ),
            RandomForestClassifier(random_state=rng)
        )

    return f

def unscaled_featureselected_n_kbest_randomforest_pipeline(n):
    def f(rng, artifacts_path):
        return make_pipeline(
            WrappedFeatureSelection(
                SelectKBest(chi2, k=n),
                artifacts_path
            ),
            RandomForestClassifier(random_state=rng)
        )

    return f

def unscaled_featureselected_RFECV_DT_randomforest_pipeline(n):
    def f(rng, artifacts_path):
        return make_pipeline(
            WrappedFeatureSelection(
                RFECV(estimator=DecisionTreeClassifier(random_state=rng),
                      cv=5,
                      scoring='matthews_corrcoef',
                      n_jobs=-3,
                      step=n),
                artifacts_path
            ),
            RandomForestClassifier(random_state=rng,n_jobs=-3)
        )

    return f

def unscaled_featureselected_RFECV_DT_randomforest_Precision_pipeline(n):
    def f(rng, artifacts_path):
        return make_pipeline(
            WrappedFeatureSelection(
                RFECV(estimator=DecisionTreeClassifier(random_state=rng),
                      cv=5,
                      scoring='precision',
                      n_jobs=-3,
                      step=n),
                artifacts_path
            ),
            RandomForestClassifier(random_state=rng,n_jobs=-3)
        )

    return f

AVAILABLE_PIPELINES = {
    "scaled-linear-ridge": scaled_linear_ridge_pipeline,
    "unscaled-linear": unscaled_linear_ridge_pipeline,
    "scaled-randomforest": scaled_randomforest_pipeline,
    "unscaled-randomforest": unscaled_randomforest_pipeline,
    "unscaled-decisiontree": unscaled_decisiontree_pipeline,
    "unscaled-catboost-01": unscaled_catboost_pipeline_creator(0.1),
    "unscaled-catboost-02": unscaled_catboost_pipeline_creator(0.2),
    "unscaled-catboost-05": unscaled_catboost_pipeline_creator(0.5),
    "unscaled-LGBM": unscaled_lgbm_pipeline,
    "unscaled-XGB": unscaled_xgboost_pipeline,
    "scaled-adaboost": scaled_adaboost_pipeline,
    "scaled-gradientboost": scaled_gradientboost_pipeline,
    "unscaled-featureselected-1-kbest-randomforest": unscaled_featureselected_n_kbest_randomforest_pipeline(1),
    "unscaled-featureselected-1-svc-randomforest": unscaled_featureselected_n_svc_randomforest_pipeline(1),
    "unscaled-featureselected-2-kbest-randomforest": unscaled_featureselected_n_kbest_randomforest_pipeline(2),
    "unscaled-featureselected-2-svc-randomforest": unscaled_featureselected_n_svc_randomforest_pipeline(2),
    "unscaled-featureselected-3-kbest-randomforest": unscaled_featureselected_n_kbest_randomforest_pipeline(3),
    "unscaled-featureselected-3-svc-randomforest": unscaled_featureselected_n_svc_randomforest_pipeline(3),
    "unscaled-featureselected-4-kbest-randomforest": unscaled_featureselected_n_kbest_randomforest_pipeline(4),
    "unscaled-featureselected-4-svc-randomforest": unscaled_featureselected_n_svc_randomforest_pipeline(4),
    "unscaled-featureselected-5-kbest-randomforest": unscaled_featureselected_n_kbest_randomforest_pipeline(5),
    "unscaled-featureselected-5-svc-randomforest": unscaled_featureselected_n_svc_randomforest_pipeline(5),
    "unscaled_featureselected_RFECV_DT_randomforest": unscaled_featureselected_RFECV_DT_randomforest_pipeline(1),
    "unscaled_featureselected_RFECV_DT_randomforest_Precision": unscaled_featureselected_RFECV_DT_randomforest_Precision_pipeline(1)
}
