import argparse
import os
import sys

from defect_modelling.defect_schema import METRIC_SETS

os.environ["KERAS_BACKEND"] = "torch"
import keras

from defect_modelling.defects_pipeline import prepare_data_set

def load_autoencoder(model_source):
    return keras.models.load_model(model_source)

def prepare_args(cmd_args):
    parser = argparse.ArgumentParser(
        prog="autoencoder-loader",
        description="Build defect prediction models"
    )
    parser.add_argument("--data_file", required=True, help="file with defects, class and commit metrics", type=str)
    parser.add_argument("--metric_set", required=True, help="which set of metrics shall be used for prediction", choices=METRIC_SETS.keys())
    parser.add_argument("--random_seed", required=False, type=int, help="random seed to use in the model building")
    parser.add_argument("--model_source", required=False, type=str, help="source for autoencoder")

    return parser.parse_args(cmd_args)

def run_with_args(cmd_args):
    args = prepare_args(cmd_args)
    # data, datafile_checksum = prepare_data_set(args.data_file, [])
    autoencoder = load_autoencoder(args.model_source)
    print(autoencoder.layers)


def run_as_main():
    run_with_args(sys.argv[1:])

if __name__ == "__main__":
    run_as_main()