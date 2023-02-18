import argparse
import datetime
import os
import random

import humanize
import pandas as pd
import time

from defects_pipeline import run_on_data as generate_defect_model, prepare_data_set, AVAILABLE_PIPELINES

EVALUATE_METRIC_SETS = ['pydriller', 'pmd', 'javametrics-numeric', 'javametrics2', 'product', 'process', 'all-non-null-numeric', "none"]
EVALUATE_MODEL_TYPES = AVAILABLE_PIPELINES.keys()
TRAINING_FRACTION = 0.8
CLASS_SET = "defects"
def prepare_args():
    parser = argparse.ArgumentParser(
        prog="defect-model-experiment",
        description="Build defect models"
    )
    parser.add_argument("--data_file", required=True, type=str, help="main data file with predictors")
    parser.add_argument("--workspace", required=True, type=str, help="workspace location for temporary files")
    parser.add_argument("--random_seed", required=False, type=int, help="Random seed to use in the model building")
    parser.add_argument("--model_count", required=True, type=int, help="How many models to generate per metric set")
    parser.add_argument("--smell_models", required=False, help="paths to all code smell models that are supposed to be predictors", nargs="*", type=str)
    parser.add_argument("--results_file_name", required=False, help="filename for output data", type=str, default="final_defects_stats.csv")

    return parser.parse_args()


def evaluate_model(workspace, model_type, data, datafile_checksum, models_dir, metric_set, index, seed, smell_models):
    model_workspace = os.path.join(workspace, "workdir", metric_set, str(index))
    os.makedirs(model_workspace, exist_ok=True)
    model_target = os.path.abspath(
        os.path.join(
            models_dir,
            "{}_{}_{}_{}.scops".format(model_type, metric_set, "smells" if len(smell_models) > 0 else "nosmells", str(index))
        )
    )

    params = ["--data_file", "NOT_USED_PASSED_DIRECTLY",
              "--metric_set", metric_set,
              "--class_set", CLASS_SET,
              "--model_target", model_target,
              "--model_type", model_type,
              "--random_seed", str(seed),
              "--training_fraction", str(TRAINING_FRACTION)
              ]

    if len(smell_models) > 0:
        params.append("--smell_models")
        params.extend(smell_models)

    print("DEFECTS_EXPERIMENT: Building model nr {} with {} from {} data".format(index + 1, "smells" if len(smell_models) > 0 else "nosmells", metric_set))
    return generate_defect_model(params, data, datafile_checksum)

def torow(model):

    real_total = model["scores"]["real"]["tp"] + \
                 model["scores"]["real"]["tn"] + \
                 model["scores"]["real"]["fp"] + \
                 model["scores"]["real"]["fn"]
    fake_total = model["scores"]["fake"]["tp"] + \
                 model["scores"]["fake"]["tn"] + \
                 model["scores"]["fake"]["fp"] + \
                 model["scores"]["fake"]["fn"]

    return [
        model["metric_set"],
        model["name"],
        model["model_type"],
        len(model["smell_models"]) > 0,
        model["scores"]["real"]["mcc"],
        model["scores"]["real"]["f1-score"],
        model["scores"]["real"]["precision"],
        model["scores"]["real"]["recall"],
        model["scores"]["real"]["accuracy"],
        model["scores"]["real"]["balanced_accuracy"],
        model["scores"]["real"]["tp"] / real_total,
        model["scores"]["real"]["fn"] / real_total,
        model["scores"]["real"]["fp"] / real_total,
        model["scores"]["real"]["tn"] / real_total,
        real_total,
        model["scores"]["fake"]["mcc"],
        model["scores"]["fake"]["f1-score"],
        model["scores"]["fake"]["precision"],
        model["scores"]["fake"]["recall"],
        model["scores"]["fake"]["accuracy"],
        model["scores"]["fake"]["balanced_accuracy"],
        model["scores"]["fake"]["tp"] / fake_total,
        model["scores"]["fake"]["fn"] / fake_total,
        model["scores"]["fake"]["fp"] / fake_total,
        model["scores"]["fake"]["tn"] / fake_total,
        fake_total,
        model["fit_time_sec"],
        model["test_time_sec"],
        model["preparation_time_sec"]
    ]

def dump_models(workdir, filename, model_list):
    target_location = os.path.abspath(os.path.join(workdir, filename))
    pd.DataFrame(
        [torow(model_list[model_num]) for model_num in range(len(model_list))],
        columns=[
            "metric_set",
            "name",
            "model_type",
            "smell_models",
            "real_mcc",
            "real_f1",
            "real_precision",
            "real_recall",
            "real_accuracy",
            "real_balanced_accuracy",
            "real_tpr",
            "real_fnr",
            "real_fpr",
            "real_fnr",
            "real_total",
            "fake_mcc",
            "fake_f1",
            "fake_precision",
            "fake_recall",
            "fake_accuracy",
            "fake_balanced_accuracy",
            "fake_tpr",
            "fake_fnr",
            "fake_fpr",
            "fake_tnr",
            "fake_total",
            "fit_time_sec",
            "test_time_sec",
            "preparation_time_sec"
        ]
    ).to_csv(target_location, index_label=["model_num"])

def run_as_main():
    args = prepare_args()
    random.seed(args.random_seed)

    models_dir = os.path.join(args.workspace, "models")
    os.makedirs(models_dir, exist_ok=True)

    prep_time_start_ts = time.monotonic()
    data, datafile_checksum = prepare_data_set(args.data_file, args.smell_models)
    prep_time_end_ts = time.monotonic()
    print("DEFECTS_EXPERIMENT: Prepared data for further processing in {}".format(humanize.naturaldelta(datetime.timedelta(seconds=prep_time_end_ts - prep_time_start_ts), minimum_unit="milliseconds")))

    all_models = []
    total = args.model_count * len(EVALUATE_MODEL_TYPES) * len(EVALUATE_METRIC_SETS)
    successful = 0
    failures = 0
    start_time = time.monotonic()
    for i in range(args.model_count):
        iteration_start_time = time.monotonic()
        seed = random.randint(0, 2**32 - 1)
        print("DEFECTS_EXPERIMENT: Evaluating {} out of {}".format(i + 1, args.model_count))
        iteration_models = []
        for metric_set in EVALUATE_METRIC_SETS:
            metric_set_start_time = time.monotonic()
            metric_models = []
            for model_type in EVALUATE_MODEL_TYPES:
                model_start_time = time.monotonic()
                print("DEFECTS_EXPERIMENT: Evaluating model '{}' for predictor set: '{}'".format(model_type, metric_set))
                try:
                    if metric_set != 'none':
                        metric_models.append(evaluate_model(args.workspace, model_type, data, datafile_checksum, models_dir, metric_set, i, seed, []))

                    metric_models.append(evaluate_model(args.workspace, model_type,data, datafile_checksum, models_dir, metric_set, i, seed, args.smell_models))
                    print("DEFECTS_EXPERIMENT: Evaluated model '{}' for predictor set: '{}'. Took: {}".format(model_type, metric_set, humanize.naturaldelta(datetime.timedelta(seconds=time.monotonic() - model_start_time))))
                    successful = successful + 1
                except Exception as e:
                    failures = failures + 1
                    print("DEFECT_EXPERIMENT: Failures: {}. Current exception {}".format(failures, e))
                print("DEFECTS_EXPERIMENT: Successes: {}, failures: {}".format(successful, failures))

            dump_models(args.workspace, "intermediate_results_{}_{}.csv".format(metric_set, i), metric_models)
            iteration_models.extend(metric_models)
            print("DEFECTS_EXPERIMENT: Evaluated all models for predictor set: '{}'. Took: {}".format( metric_set, humanize.naturaldelta(datetime.timedelta(seconds=time.monotonic() - metric_set_start_time))))

        dump_models(args.workspace, "intermediate_results_{}.csv".format(i), iteration_models)
        all_models.extend(iteration_models)


        iteration_end_time = time.monotonic()
        print("DEFECTS_EXPERIMENT: Time taken - iteration {}/{}:".format(i + 1, args.model_count), humanize.naturaldelta(datetime.timedelta(seconds=iteration_end_time - iteration_start_time), minimum_unit="milliseconds"),
              "/ total:",  humanize.naturaldelta(datetime.timedelta(seconds=iteration_end_time - start_time), minimum_unit="milliseconds"),
              "/ average:", humanize.naturaldelta(datetime.timedelta(seconds=(iteration_end_time - start_time) / (i + 1)), minimum_unit="milliseconds")
              )

    dump_models(args.workspace, args.results_file_name, all_models)

    print("DEFECTS_EXPERIMENT: Took {}, performance metrics available in {}".format(humanize.naturaldelta(datetime.timedelta(seconds=time.monotonic() - start_time)), os.path.abspath(os.path.join(args.workspace, args.results_file_name))))


if __name__ == '__main__':
    run_as_main()
#%%
