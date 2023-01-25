import argparse
import os
import random

import pandas as pd

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


def train_model(workspace, data_file, models_dir, smell, metric_set, index, seed):
    model_workspace = os.path.join(workspace, "workdir", smell, metric_set, str(index))
    os.makedirs(model_workspace, exist_ok=True)
    model_target = os.path.join(models_dir, "{}_{}_{}.scops".format(smell, metric_set, str(index)))
    params = ["--data_file", data_file,
              "--smell", smell,
              "--metric_set", metric_set,
              "--workspace", model_workspace,
              "--model_target", model_target,
              "--random_seed", str(seed)
              ]

    print("SMELLS_EXPERIMENT: Building model nr {} for {} with {} data".format(index, smell, metric_set))
    return generate_smell_model(params)

def torow(model):
    total = model["performance_metrics"]["confusion_matrix"][0][0] + model["performance_metrics"]["confusion_matrix"][1][0] + model["performance_metrics"]["confusion_matrix"][0][1] + model["performance_metrics"]["confusion_matrix"][1][1]

    return [
        model["smell"],
        model["metric_set"],
        model["name"],
        model["performance_metrics"]["mcc"],
        model["performance_metrics"]["f1-score"],
        model["performance_metrics"]["precision"],
        model["performance_metrics"]["recall"],
        model["performance_metrics"]["accuracy"],
        model["performance_metrics"]["balanced_accuracy"],
        model["performance_metrics"]["confusion_matrix"][0][0] / total,
        model["performance_metrics"]["confusion_matrix"][0][1] / total,
        model["performance_metrics"]["confusion_matrix"][1][0] / total,
        model["performance_metrics"]["confusion_matrix"][1][1] / total
    ]

def run_as_main():
    args = prepare_args()
    random.seed(args.random_seed)

    models_dir = os.path.join(args.workspace, "models")
    os.makedirs(models_dir, exist_ok=True)

    all_models = []
    for i in range(args.model_count):
        for s in EVALUATE_SMELLS:
            seed = random.randint(0, 2**32 - 1)
            for m in EVALUATE_METRIC_SETS:
                all_models.append(train_model(args.workspace, args.data_file, models_dir, s, m, i, seed))

    pd.DataFrame(
        [torow(model) for model in all_models],
        columns=[
            "smell",
            "metric_set",
            "name",
            "mcc",
            "f1",
            "precision",
            "recall",
            "accuracy",
            "balanced_accuracy",
            "tpr",
            "fnr",
            "fpr",
            "fnr"
        ]
    ).to_csv(os.path.join(args.workspace, "final_stats.csv"))


if __name__ == '__main__':
    run_as_main()