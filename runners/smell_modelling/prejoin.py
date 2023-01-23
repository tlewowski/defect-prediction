import argparse
import functools
import os.path

import pandas as pd

def prepare_args():
    parser = argparse.ArgumentParser(
        prog="smell-data-joiner",
        description="Join data from class metric calculation tools and MLCQ code smell data"
    )
    parser.add_argument("--mlcq_file", help="file with smells (in the format used by MLCQ)", type=str, required=True)
    parser.add_argument("--class_metrics_files", type=str, nargs="+", help="files with per-class metrics to merge", default=[])
    parser.add_argument("--out_file", type=str, help="Where to place joined file", required=True)

    return parser.parse_args()


def load_mlcq_data(smells_file):
    mlcq = pd.read_csv(smells_file, sep=";")
    # leave only class samples and set index
    return mlcq[mlcq["type"] == "class"].set_index(["commit_hash", "code_name"]).sort_index()


def load_class_metrics(class_files):
    files = []
    for class_file in class_files:
        f = pd.read_csv(class_file, sep=",")
        # that's because MLCQ uses dots to separate inner classes, while PMD uses $
        f["entity"] = f["entity"].transform(lambda x: x.replace("$", "."))
        # prepare index and sort for better join performance
        files.append(f.set_index(["revision", "entity"]).sort_index())

    return files

def join_data(mlcq, tool_data):
    all_tools = functools.reduce(lambda l, r: pd.merge(l, r, on=["revision", "entity"], how="outer"), tool_data).sort_index()
    print("PREJOIN: got a total of", len(all_tools.index), "records from", len(tool_data), "tools. Potential predictor columns:", all_tools.columns.values.tolist())

    # final version can't have "dropna" here
    final = all_tools.join(mlcq, on=["revision", "entity"], how="inner")

    print("PREJOIN: final dataframe has", len(final.index), "records. Potential predictors:", final.columns.values.tolist())
    return final

def run_as_main():
    args = prepare_args()
    defects = load_mlcq_data(args.mlcq_file)
    print("PREJOIN: Loaded smells data. Got", len(defects.index), "entries")
    per_tool = load_class_metrics(args.class_metrics_files)
    print("PREJOIN: Loaded class data. Got", [len(d.index) for d in per_tool], "entries")
    joined = join_data(defects, per_tool)

    out_file = os.path.abspath(args.out_file)
    joined.to_csv(out_file)
    print("PREJOIN: Successfully wrote", len(joined.index), "rows to", out_file)


if __name__ == '__main__':
    run_as_main()

#%%
