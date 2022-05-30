import argparse
import itertools
import os

from metric_differ.differ import diff_metrics
from metric_differ.metric_diff import save_diff
from metric_differ.project_history import get_project_history

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

    for commit_pair in itertools.pairwise(ordered_commits):
        print("MDMAIN: Diffing", commit_pair[0], commit_pair[1])
        diff = diff_metrics(args.metrics_path, commit_pair[0], commit_pair[1])
        save_diff(os.path.join(args.metrics_path, "diffs", commit_pair[0] + "-" + commit_pair[1]), diff)

    print("MDMAIN: Finished")

if __name__ == '__main__':
    run_as_main()
