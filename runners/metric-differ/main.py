import argparse
import csv
import os
import subprocess
from metr

def get_project_history(src: str) -> list[str]:
    args = [
        "git",
        "log",
        "--format=format:%H",
        "--all"
    ]

    return subprocess.run(args, cwd=src, capture_output=True).stdout.decode('utf-8').splitlines(keepends=False)

def diff_metrics(metrics_dir: str, later_commit: str, earlier_commit: str):

    with open(os.path.join(metrics_dir, later_commit, 'metrics.csv'), 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:


def run_as_main():
    parser = argparse.ArgumentParser(description="Calculate software project product metrics")
    parser.add_argument("--project_src_path", type=str, help="directory where project sources are", required=True)
    parser.add_argument("--metrics_path", type=str, help="path to directory with metric values", required=True)

    args = parser.parse_args()

    history = get_project_history(args.project_src_path)
    print("MDMAIN: Extracted", len(history), "commits from", args.project_src_path)

    metrics_dirs = os.listdir(args.metrics_path)
    ordered_commits = [c for c in history if c in metrics_dirs]
    print("MDMAIN: Diffing metrics for", len(metrics_dirs), "dirs (", len(ordered_commits), "commits )" )

    for commit_pair in zip(ordered_commits, ordered_commits[1:]):
        print("MDMAIN: Diffing", commit_pair[0], commit_pair[1])
        diff_metrics(args.metrics_path, commit_pair[0], commit_pair[1])

        pass

    print("MDMAIN: Finished")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_as_main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
