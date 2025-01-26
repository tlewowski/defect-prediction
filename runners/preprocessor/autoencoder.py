import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy

from defect_modelling.defect_schema import METRIC_SETS
from defect_modelling.defects_pipeline import prepare_data_set, train_test_commit_split

os.environ["KERAS_BACKEND"] = "torch"

import keras

from keras import layers
import numpy as np


def dummy_random_sampler(train_ratio, random_state):
    return lambda ds, _: ds.sample(frac=train_ratio, random_state=random_state)


def single_layer_relu(node_count: int):
    def layer(num_metrics):
        input_data = keras.Input(shape=(num_metrics,))
        encoded = layers.Dense(node_count, activation="relu")(input_data)
        decoded = layers.Dense(num_metrics, activation="relu")(encoded)
        return keras.Model(input_data, decoded)

    return layer

def dual_layer_relu(first_layer: int, second_layer: int):
    def layer(num_metrics):
        input_data = keras.Input(shape=(num_metrics,))
        layer_1 = layers.Dense(first_layer, activation="relu")(input_data)
        layer_2 = layers.Dense(second_layer, activation="relu")(layer_1)
        decode_layer_1 = layers.Dense(first_layer, activation="relu")(layer_2)
        decoded = layers.Dense(num_metrics, activation="relu")(decode_layer_1)
        return keras.Model(input_data, decoded)

    return layer


def triple_layer_relu(first_layer: int, second_layer: int, third_layer: int):
    def layer(num_metrics):
        input_data = keras.Input(shape=(num_metrics,))
        layer_1 = layers.Dense(first_layer, activation="relu")(input_data)
        layer_2 = layers.Dense(second_layer, activation="relu")(layer_1)
        layer_3 = layers.Dense(third_layer, activation="relu")(layer_2)
        decode_layer_1 = layers.Dense(second_layer, activation="relu")(layer_3)
        decode_layer_2 = layers.Dense(first_layer, activation="relu")(decode_layer_1)
        decoded = layers.Dense(num_metrics, activation="relu")(decode_layer_2)
        return keras.Model(input_data, decoded)

    return layer


def quadruple_layer_relu(first_layer: int, second_layer: int, third_layer: int, fourth_layer: int):
    def layer(num_metrics):
        input_data = keras.Input(shape=(num_metrics,))
        layer_1 = layers.Dense(first_layer, activation="relu")(input_data)
        layer_2 = layers.Dense(second_layer, activation="relu")(layer_1)
        layer_3 = layers.Dense(third_layer, activation="relu")(layer_2)
        layer_4 = layers.Dense(fourth_layer, activation="relu")(layer_3)
        decode_layer_1 = layers.Dense(fourth_layer, activation="relu")(layer_4)
        decode_layer_2 = layers.Dense(second_layer, activation="relu")(decode_layer_1)
        decode_layer_3 = layers.Dense(first_layer, activation="relu")(decode_layer_2)
        decoded = layers.Dense(num_metrics, activation="relu")(decode_layer_3)
        return keras.Model(input_data, decoded)

    return layer

AUTOENCODER_ARCHITECTURES = {
    "single-layer-10-relu": single_layer_relu(10),
    "single-layer-5-relu": single_layer_relu(5),
    "single-layer-3-relu": single_layer_relu(3),
    "single-layer-1-relu": single_layer_relu(1),
    "dual-layer-30-10-relu": dual_layer_relu(30, 10),
    "dual-layer-20-10-relu": dual_layer_relu(20, 10),
    "dual-layer-30-5-relu": dual_layer_relu(30, 5),
    "dual-layer-20-5-relu": dual_layer_relu(20, 5),
    "dual-layer-30-3-relu": dual_layer_relu(30, 3),
    "dual-layer-20-3-relu": dual_layer_relu(20, 3),
    "triple-layer-40-20-10-relu": triple_layer_relu(40, 20, 10),
    "triple-layer-30-20-10-relu": triple_layer_relu(30, 20, 10),
    "triple-layer-30-20-5-relu": triple_layer_relu(30, 20, 5),
    "triple-layer-40-20-5-relu": triple_layer_relu(40, 20, 5),
    "triple-layer-40-15-5-relu": triple_layer_relu(40, 15, 5),
    "triple-layer-30-15-3-relu": triple_layer_relu(30, 15, 3),
    "quadruple-layer-40-20-10-5-relu": quadruple_layer_relu(40, 20, 10, 5),
    "quadruple-layer-40-15-8-3-relu": quadruple_layer_relu(40, 15, 8, 3),
    "quadruple-layer-40-15-8-1-relu": quadruple_layer_relu(40, 15, 8, 1)
}



def build_autoencoder(x_train, x_test, architecture, global_random_state):
    x_train = x_train.to_numpy()
    x_test = x_test.to_numpy()
    rows, cols = x_train.shape

    keras.utils.set_random_seed(int(global_random_state.integers(low=0, high=2**32-1, size=1)[0]))

    autoencoder = AUTOENCODER_ARCHITECTURES[architecture](cols)

    autoencoder.compile(optimizer="adam", loss="mean_squared_error", metrics=["root_mean_squared_error"])

    x_train = x_train.astype('float32') / 255.0
    x_train = x_train.reshape((len(x_train), np.prod(x_train.shape[1:])))

    autoencoder.fit(x_train, x_train, epochs=4, batch_size=500, shuffle=True, validation_data=(x_test, x_test))

    return autoencoder

def train_autoencoder(args, data, datafile_checksum, training_sampler = None):
    preparation_start_ts = time.monotonic()
    print("AUTOENCODER_PIPELINE: Running with", len(data.index), "entries")
    global_random_state = numpy.random.default_rng()
    if args.random_seed is not None:
        global_random_state = numpy.random.default_rng(args.random_seed)

    if training_sampler is None:
        sampler = dummy_random_sampler(args.training_fraction, global_random_state)
    else:
        sampler = training_sampler

    metric_set = METRIC_SETS[args.metric_set].copy()
    temp_metric_set = metric_set.copy()
    temp_metric_set.extend(["revision"])
    relevant_data = data.loc[:, temp_metric_set]

    training_revisions, testing_revisions = train_test_commit_split(data, [], sampler)
    training_data = relevant_data[relevant_data.revision.isin(training_revisions.revision)]
    testing_data = relevant_data[relevant_data.revision.isin(testing_revisions.revision)]

    fitting_start_ts = time.monotonic()
    print("AUTOENCODER_PIPELINE: Preparation took: {} seconds".format(fitting_start_ts - preparation_start_ts))
    print("AUTOENCODER_PIPELINE: Autoencoder training will be triggered with {} samples from {} revisions for training. Using columns: {}, optimizing: {}"
          .format(len(training_data.index), len(training_revisions.index), metric_set, args.architecture))

    autoencoder = build_autoencoder(training_data.loc[:, metric_set], testing_data.loc[:, metric_set], args.architecture, global_random_state)

    fitting_end_ts = time.monotonic()

    print("AUTOENCODER_PIPELINE: Fitting took: {} seconds".format(fitting_end_ts - fitting_start_ts))
    return autoencoder


def prepare_args(cmd_args):
    parser = argparse.ArgumentParser(
        prog="autoencoder-builder",
        description="Build defect prediction models"
    )
    parser.add_argument("--data_file", required=True, help="file with defects, class and commit metrics", type=str)
    parser.add_argument("--metric_set", required=True, help="which set of metrics shall be used for prediction", choices=METRIC_SETS.keys())
    parser.add_argument("--random_seed", required=False, type=int, help="random seed to use in the model building")
    parser.add_argument("--architecture", required=False, type=str, help="architecture for autoencoder", choices=[x for x in AUTOENCODER_ARCHITECTURES.keys()])
    parser.add_argument("--training_fraction", required=False, type=float, help="fraction of data set to be used in training", default=0.8)
    parser.add_argument("--model_target", required=False, type=str, help="location where model will be saved")
    parser.add_argument("--save_models", type=bool, action=argparse.BooleanOptionalAction, help="save built models for future evaluation", default=True)
    parser.add_argument("--iteration_id", type=int, help="iteration identifier")

    return parser.parse_args(cmd_args)

def save_metadata(autoencoder, args, target_path):
    with open(target_path, 'w') as f:
        f.write(json.dumps({
            "seed": args.random_seed,
            "architecture": args.architecture,
            "metric_set": args.metric_set,
            "training_fraction": args.training_fraction,
            "activation_layers": len(autoencoder.layers) - 1,
            "last_encoding_layer":  (len(autoencoder.layers) - 1) / 2
        }))


def run_with_args(cmd_args):
    args = prepare_args(cmd_args)
    data, datafile_checksum = prepare_data_set(args.data_file, [])
    autoencoder = train_autoencoder(args, data, datafile_checksum)
    if args.save_models:
        autoencoder.save(Path(args.model_target) / f"autoencoder_{args.architecture}_{args.iteration_id}.keras")
        save_metadata(autoencoder, args, Path(args.model_target) / f"metadata_autoencoder_{args.architecture}_{args.iteration_id}.json")

def run_as_main():
    run_with_args(sys.argv[1:])

def load(path):
    with np.load(path, allow_pickle=True) as f:
        x_train, y_train = f["x_train"], f["y_train"]
        x_test, y_test = f["x_test"], f["y_test"]

        return (x_train, y_train), (x_test, y_test)

if __name__ == "__main__":
    run_as_main()