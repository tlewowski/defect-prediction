import argparse
import dataclasses
import datetime
import functools
import hashlib
import os.path
import sys
import time

os.environ["KERAS_BACKEND"] = "torch"

import keras
import numpy
import skops.io
import humanize
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, \
    balanced_accuracy_score, matthews_corrcoef, confusion_matrix

from defect_schema import METRIC_SETS, CLASS_SETS
from smell_modelling.evaluate import evaluate_on_data, select_columns
from defect_utils import cleanse
from smell_modelling.smell_utils import impute_data
from modelling_pipelines import AVAILABLE_PIPELINES


def prepare_args(cmd_args):
    parser = argparse.ArgumentParser(
        prog="defect-model-builder",
        description="Build defect prediction models"
    )
    parser.add_argument("--data_file", required=True, help="file with defects, class and commit metrics", type=str)
    parser.add_argument("--metric_set", required=True, help="which set of metrics shall be used for prediction", choices=METRIC_SETS.keys())
    parser.add_argument("--class_set", required=True, help="which features shall be treated as the class columns", choices=CLASS_SETS.keys())
    parser.add_argument("--smell_models", required=False, help="paths to all code smell models that are supposed to be predictors", nargs="*", type=str, default=[])
    parser.add_argument("--random_seed", required=False, type=int, help="random seed to use in the model building")
    parser.add_argument("--training_fraction", required=False, type=float, help="fraction of data set to be used in training", default=0.8)
    parser.add_argument("--model_target", required=False, type=str, help="location where model will be saved")
    parser.add_argument("--model_type", required=True, type=str, help="which pipeline to use for modelling", choices=AVAILABLE_PIPELINES.keys())
    parser.add_argument("--save_models", type=bool, action=argparse.BooleanOptionalAction, help="save built models for future evaluation", default=True)
    parser.add_argument("--save_artifacts", type=bool, action=argparse.BooleanOptionalAction, help="save artifacts created by intermediate pipeline steps", default=True)
    parser.add_argument("--pretransformer_path", type=str, help="Path to model for pre-transforming data", required=False)
    parser.add_argument("--pretransformer_mode", type=str, help="Mode for the pretransformer", required=False, choices=["featureselection", "denoising"])

    return parser.parse_args(cmd_args)

def new_pipeline(model_type, rng, artifacts_location):
    random_state = rng.integers(0, 2**32-1)
    return AVAILABLE_PIPELINES[model_type](random_state, artifacts_location)

def run_ml_process(predictors, classes, model_type, rng, artifacts_location):
    pipeline = new_pipeline(model_type, rng, artifacts_location)

    print("DEFECT_PIPELINE: Triggering training for ", model_type, ".Got", len(predictors), f"entries for training")

    calculation_start_time = time.monotonic()
    pipeline.fit(predictors, classes)
    calculation_end_time = time.monotonic()

    print("DEFECT_PIPELINE: Finished training in ", humanize.naturaldelta(datetime.timedelta(seconds=calculation_end_time-calculation_start_time), minimum_unit="milliseconds"))
    return pipeline

def test_ml_pipeline(pipeline, test_data, metric_set, class_set):
    revisions = test_data.loc[:, ["revision"]]
    test_predictors = test_data.loc[:, metric_set]
    classes = test_data.loc[:, class_set].astype('int')
    predictions = pipeline.predict(test_predictors).astype('int')

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

    # Removing, because entries for Hadoop are broken - none are marked as "buggy"
    return data[data["project"] != "hadoop"]

def select_relevant_columns(data, metric_set, class_set, allow_drop=True):
    all_cols = []
    all_cols.extend(metric_set)
    all_cols.extend(class_set)
    all_cols.append("revision")

    selected = data.loc[:, all_cols]
    selected[class_set] = selected[class_set].applymap(lambda x: 1 if x else 0)
    dropped = selected.dropna()
    print("DEFECT_UTILS: After dropping NAs, {} reviews/samples left (from {} initially)".format(len(dropped.index), len(selected.index)))
    if len(selected.index) != len(dropped.index):
        print("DEFECT_UTILS: !!!! Warning! Detected N/A samples! If they are not dropped later on, "
              "results may be surprising! Initial:{}, final: {}. Example rows: ".format(
            len(selected.index), len(selected.index), selected[dropped.isna().any(axis=1)])
        )
        if not allow_drop:
            raise Exception("Some samples were dropped at preprocessing, but dropping was not allowed")


    return dropped.drop_duplicates()


def calculate_smells(data, smell_models):
    prepared_data = impute_data(data)
    results = [evaluate_on_data(prepared_data, skops.io.load(model, trusted=True)) for model in smell_models]
    return functools.reduce(lambda l, r: l.join(r, how="outer"), results).sort_index()


def train_test_commit_split(data, classes, sampler):
    cols = ["revision", "project"]
    cols.extend(classes)
    revision_data = data.loc[:, cols].drop_duplicates()

    train_revisions = sampler(revision_data, classes)
    test_revisions = pd.concat([revision_data, train_revisions]).drop_duplicates(keep=False)
    print("DEFECT_PIPELINE: After split from", len(revision_data.index),"got", len(train_revisions.index), "samples for training and", len(test_revisions.index), "samples for training")
    return train_revisions, test_revisions

def prepare_data_set(data_file, smell_models):
    preparation_start_ts = time.monotonic()
    input_file = os.path.abspath(data_file)
    data = load_input(input_file)

    with open(data_file, "rb") as f:
        datafile_checksum = hashlib.sha256(f.read()).hexdigest()

    smell_adding_start_ts = time.monotonic()
    print("DEFECT_PIPELINE_PREP: Loaded data. Got", len(data.index), "entries from", input_file, "in", humanize.naturaldelta(datetime.timedelta(seconds=smell_adding_start_ts-preparation_start_ts), minimum_unit="milliseconds"))
    if smell_models:
        smell_predictors = calculate_smells(data, smell_models)
        data = data.join(smell_predictors)
        print("DEFECT_PIPELINE_PREP: Added data from {} smell models: {}. Took: {}".format(
            len(smell_models),
            smell_predictors.columns.values.tolist(),
            humanize.naturaldelta(datetime.timedelta(seconds=time.monotonic()-smell_adding_start_ts), minimum_unit="milliseconds"))
        )

    print("DEFECT_PIPELINE_PREP: Finished basic data preparation in", humanize.naturaldelta(datetime.timedelta(seconds=time.monotonic()-preparation_start_ts), minimum_unit="milliseconds"))
    return cleanse(data), datafile_checksum

def random_sampler(train_ratio, random_state):
    return lambda ds, classes: ds.groupby(classes).sample(frac=train_ratio, random_state=random_state)


def cut_to_featureselection(pretransformer):
    featureselection_final_layer = int((len(pretransformer.layers) - 1) / 2)
    return keras.Sequential(pretransformer.layers[:featureselection_final_layer+1])

@dataclasses.dataclass
class Pretransformer:
    model: keras.Model

    def pretransform(self, metric_set, data):
        input_data = data.loc[:, metric_set].to_numpy()
        altered = self.model.predict(input_data)
        _, cols = altered.shape

        additions = data.drop(metric_set, axis=1)
        with_classes = numpy.concatenate((altered, additions.to_numpy()), axis=1)
        df = pd.DataFrame(with_classes)

        mapping = {c: additions.columns[c - cols] for c in range(cols, cols+len(additions.columns)) }
        df = df.rename(columns=mapping)

        return df, list(df.columns)[:cols]

def load_pretransformer(path, mode):
    model = keras.models.load_model(path)
    if mode == "featureselection":
        first_half = cut_to_featureselection(model)
        return Pretransformer(first_half)
    elif mode == "denoising":
        return Pretransformer(model)
    else:
        raise ValueError(f"Unknown pretransformer mode: {mode}")


def run_on_data(cmd_args, data, datafile_checksum, training_sampler = None):
    preparation_start_ts = time.monotonic()
    args = prepare_args(cmd_args)
    print("DEFECT_PIPELINE: Running with", len(data.index), "entries")
    global_random_state = numpy.random.default_rng()
    if args.random_seed is not None:
        global_random_state = numpy.random.default_rng(args.random_seed)

    artifacts_location = None
    if args.save_artifacts:
        artifacts_location = args.model_target + ".artifacts"
        os.makedirs(artifacts_location, exist_ok=True)

    if training_sampler is None:
        sampler = random_sampler(args.training_fraction, global_random_state)
    else:
        sampler = training_sampler

    metric_set = METRIC_SETS[args.metric_set].copy()
    class_set = CLASS_SETS[args.class_set].copy()
    metric_set.extend([col for col in data.columns.values.ravel() if col.startswith("SMELL_") and len(args.smell_models) > 0])
    relevant_data = select_relevant_columns(data, metric_set, class_set)

    training_revisions, testing_revisions = train_test_commit_split(data, class_set, sampler)
    training_data = relevant_data[relevant_data.revision.isin(training_revisions.revision)]
    testing_data = relevant_data[relevant_data.revision.isin(testing_revisions.revision)]

    if args.pretransformer_path is not None:
        print(f"DEFECT_PIPELINE: using pretransformer from {args.pretransformer_path} to adjust input data")
        pretransforming_start_ts = time.monotonic()
        pretransformer = load_pretransformer(args.pretransformer_path, args.pretransformer_mode)
        training_data, cols = pretransformer.pretransform(metric_set, training_data)
        testing_data, _ = pretransformer.pretransform(metric_set, testing_data)
        metric_set = cols
        class_data = training_data.loc[:, class_set].values.ravel()

        pretransforming_end_ts = time.monotonic()
        print(f"DEFECT_PIPELINE: pretransformation of data took {humanize.naturaldelta(pretransforming_end_ts - pretransforming_start_ts)}. Current metric set: {metric_set}, columns: {training_data.columns}")
    else:
        class_data = training_data.loc[:, class_set].values.ravel()


    training_data = training_data.reset_index(drop=True)

    fitting_start_ts = time.monotonic()
    print("DEFECT_PIPELINE: ML pipeline will be triggered with {} samples from {} revisions for training. Using predictor columns: {} for predicting {}"
          .format(len(training_data.index), len(training_revisions.index), metric_set, class_set))
    pipeline = run_ml_process(training_data.loc[:, metric_set], class_data.astype('int'), args.model_type, global_random_state, artifacts_location)

    print("DEFECT_PIPELINE: Testing will be executed with {} samples from {} revisions".format(len(testing_data.index), len(testing_revisions.index)))

    testing_start_ts = time.monotonic()
    scores = test_ml_pipeline(pipeline, testing_data, metric_set, class_set)

    process_end_ts = time.monotonic()

    output = {
        "scores": scores,
        "model": pipeline,
        "model_type": args.model_type,
        "metric_set": args.metric_set,
        "final_metric_set": metric_set,
        "pretransformer": args.pretransformer_path,
        "pretransformer_mode": args.pretransformer_mode,
        "class_set": args.class_set,
        "name": "DEFECTS_" + os.path.basename(args.model_target or "UNNAMED"),
        "training_fraction": args.training_fraction,
        "data_file": args.data_file,
        "data_file_sha256_checksum": datafile_checksum,
        "smell_models": args.smell_models,
        "fit_time_sec": testing_start_ts - fitting_start_ts,
        "preparation_time_sec": fitting_start_ts - preparation_start_ts,
        "test_time_sec": process_end_ts - testing_start_ts
    }

    if args.model_target is not None and args.save_models:
        skops.io.dump(output, os.path.abspath(args.model_target))

    return output

def run_with_args(cmd_args):
    args = prepare_args(cmd_args)
    data, datafile_checksum = prepare_data_set(args.data_file, args.smell_models)
    run_on_data(cmd_args, data, datafile_checksum)

def run_as_main():
    run_with_args(sys.argv[1:])


if __name__ == '__main__':
    run_as_main()
