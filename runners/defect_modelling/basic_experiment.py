import argparse
import datetime
import os
import random

import humanize
import pandas as pd
import time

from defects_pipeline import run_with_args as generate_defect_model

EVALUATE_METRIC_SETS = ['pydriller', 'pmd', 'javametrics-numeric', 'javametrics2', 'product', 'process', 'all-non-null-numeric']
TRAINING_FRACTION = 0.8
CLASS_SET = "defects"
def prepare_args():
    parser = argparse.ArgumentParser(
        prog="defect-model-experiment",
        description="Build defect models"
    )
    parser.add_argument("--data_file", required=True, type=str, help="")
    parser.add_argument("--workspace", required=True, type=str, help="workspace location for temporary files")
    parser.add_argument("--random_seed", required=False, type=int, help="Random seed to use in the model building")
    parser.add_argument("--model_count", required=True, type=int, help="How many models to generate per metric set")
    parser.add_argument("--smell_models", required=False, help="paths to all code smell models that are supposed to be predictors", nargs="*", type=str)

    return parser.parse_args()


def evaluate_model(workspace, data_file, models_dir, metric_set, index, seed, smell_models):
    model_workspace = os.path.join(workspace, "workdir", metric_set, str(index))
    os.makedirs(model_workspace, exist_ok=True)
    model_target = os.path.abspath(
        os.path.join(
            models_dir,
            "{}_{}_{}.scops".format(metric_set, "smells" if len(smell_models) > 0 else "nosmells", str(index))
        )
    )

    params = ["--input_data", os.path.abspath(data_file),
              "--metric_set", metric_set,
              "--class_set", CLASS_SET,
              "--model_target", model_target,
              "--random_seed", str(seed),
              "--training_fraction", TRAINING_FRACTION
              ]

    if len(smell_models) > 0:
        params.append("--smell_models")
        params.extend(smell_models)

    print("SMELLS_EXPERIMENT: Building model nr {} with {} from {} data".format(index, "smells" if len(smell_models) > 0 else "nosmells", metric_set))
    return generate_defect_model(params)

def torows(model, model_num):

    real_total = model["scores"]["real"]["tp"] + \
                 model["scores"]["real"]["tn"] + \
                 model["scores"]["real"]["fp"] + \
                 model["scores"]["real"]["fn"]
    fake_total = model["scores"]["fake"]["tp"] + \
                 model["scores"]["fake"]["tn"] + \
                 model["scores"]["fake"]["fp"] + \
                 model["scores"]["fake"]["fn"]

    return [
        model_num,
        model["metric_set"],
        model["name"],
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
        model["fit_time_ms"],
        model["test_time_ms"],
        model["preparation_time_ms"]
    ]

def run_as_main():
    args = prepare_args()
    random.seed(args.random_seed)

    models_dir = os.path.join(args.workspace, "models")
    os.makedirs(models_dir, exist_ok=True)

    all_models = []
    start_time = time.monotonic()
    for i in range(args.model_count):
        iteration_start_time = time.monotonic()
        seed = random.randint(0, 2**32 - 1)
        print("DEFECTS_EXPERIMENT: Evaluating {} out of {}".format(i + 1, args.model_count))
        for m in EVALUATE_METRIC_SETS:
            print("DEFECTS_EXPERIMENT: Evaluating {}".format(m))
            all_models.append(evaluate_model(args.workspace, args.data_file, models_dir, m, i, seed, []))
            all_models.append(evaluate_model(args.workspace, args.data_file, models_dir, m, i, seed, args.smell_models))

        iteration_end_time = time.monotonic()
        print("DEFECTS_EXPERIMENT: Time taken - iteration {}:".format(i + 1), humanize.naturaldelta(datetime.timedelta(seconds=iteration_end_time - iteration_start_time), minimum_unit="milliseconds"),
              "/ total:",  humanize.naturaldelta(datetime.timedelta(seconds=iteration_end_time - start_time), minimum_unit="milliseconds"),
              "/ average:", humanize.naturaldelta(datetime.timedelta(seconds=(iteration_end_time - start_time) / (i + 1)), minimum_unit="milliseconds")
              )

    full_frame_location = os.path.abspath(os.path.join(args.workspace, "final_defects_stats.csv"))
    pd.DataFrame(
        [row for model_num in range(len(all_models)) for row in torows(all_models[model_num], model_num)],
        columns=[
            "model_num",
            "metric_set",
            "name",
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
            "fit_time_ms",
            "test_time_ms",
            "preparation_time_ms"
        ]
    ).to_csv(full_frame_location)

    print("DEFECTS_EXPERIMENT: Took {}, performance metrics available in {}".format(humanize.naturaldelta(datetime.timedelta(seconds = time.monotonic() - start_time)), full_frame_location))


if __name__ == '__main__':
    run_as_main()
#%%
