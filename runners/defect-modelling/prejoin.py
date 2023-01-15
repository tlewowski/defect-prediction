import argparse
import functools
import os.path

import pandas as pd

def prepare_args():
    parser = argparse.ArgumentParser(
        prog="defect-data-joiner",
        description="Join data from class metric calculation tools and ApacheJIT defect data"
    )
    parser.add_argument("--defects_file", help="file with defects and commit metrics", type=str, required=True)
    parser.add_argument("--class_metrics_files", type=str, nargs="+", help="files with per-class metrics to merge", default=[])
    parser.add_argument("--out_file", type=str, help="Where to place joined file", required=True)

    return parser.parse_args()


def load_defects_data(defects_file):
    apachejit = pd.read_csv(defects_file, sep=",")
    # remove "apache/" prefix and prepare index - sort for better join performance
    apachejit["project"] = apachejit["project"].apply(lambda p: p[7:])
    return apachejit.set_index(["project", "commit_id"]).sort_index()


def load_class_metrics(class_files):
    # prepare index and sort for better join performance
    return [pd.read_csv(class_file, sep=",").set_index(["project", "revision", "entity"]).sort_index() for class_file in class_files]

def join_data(apachejit, tool_data):
    all_tools = functools.reduce(lambda l, r: pd.merge(l, r, on=["project", "revision", "entity"], how="outer"), tool_data).sort_index()
    print("PREJOIN: got a total of", len(all_tools.index), "records from", len(tool_data), "tools. Potential predictor columns:", all_tools.columns.values.tolist())

    # final version can't have "dropna" here
    final = all_tools.join(apachejit, on=["project", "revision"], how="outer")

    print("PREJOIN: final dataframe has", len(final.index), "records. Potential predictors:", final.columns.values.tolist())
    return final

def run_as_main():
    args = prepare_args()
    defects = load_defects_data(args.defects_file)
    print("PREJOIN: Loaded defect and commit data. Got", len(defects.index), "entries")
    per_tool = load_class_metrics(args.class_metrics_files)
    print("PREJOIN: Loaded class data. Got", [len(d.index) for d in per_tool], "entries")
    joined = join_data(defects, per_tool)

    out_file = os.path.abspath(args.out_file)
    joined.to_csv(out_file)
    print("PREJOIN: Successfully wrote", len(joined.index), "rows to", out_file)


if __name__ == '__main__':
    run_as_main()

#%%
