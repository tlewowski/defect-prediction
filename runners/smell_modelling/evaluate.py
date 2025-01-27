import argparse

import pandas as pd
import skops.io

from .smell_utils import cleanse
from .smell_schema import METRIC_SETS

def prepare_args():
    parser = argparse.ArgumentParser(
        prog="smell-model-evaluator",
        description="Build code smell models"
    )
    parser.add_argument("--data_file", required=True, type=str)
    parser.add_argument("--model_file", required=True, type=str)
    return parser.parse_args()

def prepare_data(input_df, model_data):
    return cleanse(input_df, METRIC_SETS[model_data["metric_set"]])

def select_columns(input_df, model_data):
    return input_df.loc[:, METRIC_SETS[model_data["metric_set"]]]

def evaluate_on_data(input_data, model_data):
    return pd.DataFrame(
        model_data["model"].predict(select_columns(input_data, model_data)),
        index=input_data.index.values,
        columns=[model_data["name"]]
    )
def evaluate_frame(input_df, model_data):
    input_data = cleanse(input_df, METRIC_SETS[model_data["metric_set"]], False)
    return evaluate_on_data(input_data, model_data)


def evaluate_data(data_file, model_file):
    model_data = skops.io.load(model_file, trusted=True)
    data = pd.read_csv(data_file)
    return evaluate_frame(data[data["smell"] == model_data["smell"]], model_data)


def run_as_main():
    args = prepare_args()
    evaluate_data(args.data_file, args.model_file)


if __name__ == "__main__":
    run_as_main()