import argparse

import pandas as pd

def prepare_args():
    parser = argparse.ArgumentParser(
        prog="smell-model-builder",
        description="Build code smell models"
    )
    parser.add_argument("-r", "--reviews", required=True, type=str)
    parser.add_argument("-c", "--class-metrics", required=True, type=str)
    parser.add_argument("-m", "--method-metrics", required=True, type=str)
    parser.add_argument("-i", "--include-smell", action="append", required=True, type=str)
    return parser.parse_args()



ef load_mlcq_samples(reviews_file):
    return pd.read_csv(reviews_file, sep=";")
def run_as_main():
    args = prepare_args()
    reviews = load_mlcq_samples(args.reviews)
    class_metrics = load_class_metrics(args.class_metrics)
    method_metrics = load_method_metrics(args.method_metrics)
    dataset = join(samples, reviews)
    assign_severities(dataset)


if __name__ == '__main__':
    run_as_main()
