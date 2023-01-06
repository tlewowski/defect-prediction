import argparse
import os


class MetricFile:
    def __init__(self, project: str, revision: str, full_path: str):
        self.project = project
        self.revision = revision
        self.full_path = full_path


def parser():
    p = argparse.ArgumentParser(description="Merge metrics from various projects and revisions into single CSV file")
    p.add_argument("--metrics_root", type=str, help="root location where metrics are stored", required=True)
    p.add_argument("--target_file", type=str, help="location of final file with metrics", required=True)
    return p

def collect_metric_files(metrics_root: str) -> list[MetricFile]:
    projects = os.listdir(metrics_root)
    metric_files = []
    for project in projects:
        project_path = os.path.join(metrics_root, project)
        if not os.path.isdir(project_path):
            continue

        revisions = os.listdir(project_path)
        for revision in revisions:
            metrics_path = os.path.join(metrics_root, project, revision, "metrics.csv")
            if os.path.isfile(metrics_path):
                metric_files.append(MetricFile(project, revision, metrics_path))

    return metric_files

def run_as_main():
    args = parser().parse_args()
    metric_files = collect_metric_files(args.metrics_root)

    headers_written = False
    with open(args.target_file, mode="w", encoding="utf-8") as f:
        for metric_file in metric_files:
            with open(metric_file.full_path, mode="r", encoding="utf-8") as m:
                lines = m.readlines()
                if not headers_written:
                    f.write("project,revision,{}\n".format(lines[0].strip()))
                    headers_written = True

                f.writelines(["{},{},{}\n".format(metric_file.project, metric_file.revision, line.strip()) for line in lines[1:] if line.strip() != ""])

if __name__ == "__main__":
    run_as_main()