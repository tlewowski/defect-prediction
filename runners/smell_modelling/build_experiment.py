import argparse
import datetime
import os
import random

import humanize
import pandas as pd
import time

from smells import run_with_args as generate_smell_model

EVALUATE_METRIC_SETS = ['pmd', 'javametrics-numeric', 'all-non-null-numeric']
EVALUATE_SMELLS = ['blob', 'data class']

def prepare_args():
    parser = argparse.ArgumentParser(
        prog="smell-model-experiment",
        description="Build code smell models"
    )
    parser.add_argument("--data_file", required=True, type=str, help="")
    parser.add_argument("--workspace", required=True, type=str, help="workspace location for temporary files")
    parser.add_argument("--random_seed", required=False, type=int, help="Random seed to use in the model building")
    parser.add_argument("--model_count", required=True, type=int, help="How many models to generate")

    return parser.parse_args()


def cv_evaluate_model(workspace, data_file, models_dir, smell, metric_set, index, seed):
    model_workspace = os.path.join(workspace, "workdir", smell, metric_set, str(index))
    os.makedirs(model_workspace, exist_ok=True)
    model_target = os.path.abspath(os.path.join(models_dir, "{}_{}_{}.scops".format(smell, metric_set, str(index))))
    params = ["--data_file", os.path.abspath(data_file),
              "--smell", smell,
              "--metric_set", metric_set,
              "--workspace", model_workspace,
              "--model_target", model_target,
              "--random_seed", str(seed),
              "--cv", str(10)
              ]

    print("SMELLS_EXPERIMENT: Building model nr {} for {} with {} data".format(index, smell, metric_set))
    return generate_smell_model(params)

def torows(model, model_num):
    total = model["performance_metrics"]["test_tp"][0] + \
            model["performance_metrics"]["test_tn"][0] + \
            model["performance_metrics"]["test_fp"][0] + \
            model["performance_metrics"]["test_fn"][0]

    return [[
        model_num,
        model["smell"],
        model["metric_set"],
        model["name"],
        i,
        model["performance_metrics"]["test_mcc"][i],
        model["performance_metrics"]["test_f1-score"][i],
        model["performance_metrics"]["test_precision"][i],
        model["performance_metrics"]["test_recall"][i],
        model["performance_metrics"]["test_accuracy"][i],
        model["performance_metrics"]["test_balanced_accuracy"][i],
        model["performance_metrics"]["test_tp"][i] / total,
        model["performance_metrics"]["test_fn"][i] / total,
        model["performance_metrics"]["test_fp"][i] / total,
        model["performance_metrics"]["test_tn"][i] / total,
        model["performance_metrics"]["fit_time"][i] / total,
        model["performance_metrics"]["score_time"][i] / total
    ] for i in range(model["cv"])]

def run_as_main():
    args = prepare_args()
    random.seed(args.random_seed)

    models_dir = os.path.join(args.workspace, "models")
    os.makedirs(models_dir, exist_ok=True)

    all_models = []
    start_time = time.monotonic()
    for i in range(args.model_count):
        iteration_start_time = time.monotonic()
        for s in EVALUATE_SMELLS:
            seed = random.randint(0, 2**32 - 1)
            for m in EVALUATE_METRIC_SETS:
                print("SMELLS_EXPERIMENT: Evaluating {} out of {}".format(i + 1, args.model_count))
                all_models.append(cv_evaluate_model(args.workspace, args.data_file, models_dir, s, m, i, seed))
        iteration_end_time = time.monotonic()
        print("SMELLS_EXPERIMENT: Time taken - iteration {}:".format(i + 1), humanize.naturaldelta(datetime.timedelta(seconds=iteration_end_time - iteration_start_time), minimum_unit="milliseconds"),
              "/ total:",  humanize.naturaldelta(datetime.timedelta(seconds=iteration_end_time - start_time), minimum_unit="milliseconds"),
              "/ average:", humanize.naturaldelta(datetime.timedelta(seconds=(iteration_end_time - start_time) / (i +1 )), minimum_unit="milliseconds")
        )


    # magical list comprehension
    # acc = []
    # for model_num in range(len(all_models)):
    #   for row in torows(all_models[model_num], model_num):
    #     acc.append(row)
    #
    full_frame_location = os.path.abspath(os.path.join(args.workspace, "final_stats.csv"))
    pd.DataFrame(
        [row for model_num in range(len(all_models)) for row in torows(all_models[model_num], model_num)],
        columns=[
            "model_num",
            "smell",
            "metric_set",
            "name",
            "fold_num",
            "mcc",
            "f1",
            "precision",
            "recall",
            "accuracy",
            "balanced_accuracy",
            "tpr",
            "fnr",
            "fpr",
            "tnr",
            "fit_time",
            "score_time"
        ]
    ).to_csv(full_frame_location)

    print("SMELLS_EXPERIMENT: Took {}, performance metrics available in {}".format(humanize.naturaldelta(datetime.timedelta(seconds = time.monotonic() - start_time)), full_frame_location))


if __name__ == '__main__':
    run_as_main()
#%%
