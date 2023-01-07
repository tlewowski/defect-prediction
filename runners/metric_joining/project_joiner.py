import argparse
import csv
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


class SameToolMetrics:
    def __init__(self, metric_file, header, rows):
        self.header = header
        self.header_lookup = dict(zip(header, range(len(header))))
        self.rows = rows
        self.metric_file = metric_file

    def row_conforming(self, row, final_headers):
        return [self.value_for(row, v) for v in final_headers]

    def value_for(self, row, metric):
        if metric == 'project':
            return self.metric_file.project
        if metric == 'revision':
            return self.metric_file.revision

        if metric in self.header_lookup:
            return row[self.header_lookup[metric]]
        else:
            return None


def calculate_final_headers(metrics: list[SameToolMetrics]) -> list[str]:
    return list(dict.fromkeys([h for m in metrics for h in m.header]))


def run_as_main():
    args = parser().parse_args()
    metric_files = collect_metric_files(args.metrics_root)

    with open(args.target_file, mode="w", encoding="utf-8", newline="") as f:
        all_metrics_for_tool = []
        for metric_file in metric_files:
            with open(metric_file.full_path, mode="r", encoding="utf-8") as m:
                reader = csv.reader(m, delimiter=',')
                header = next(reader)
                all_metrics_for_tool.append(SameToolMetrics(metric_file, header, [r for r in reader]))

        final_headers = ["project", "revision"]
        final_headers.extend(calculate_final_headers(all_metrics_for_tool))
        data = [m.row_conforming(r, final_headers) for m in all_metrics_for_tool for r in m.rows]

        writer = csv.writer(f)
        writer.writerow(final_headers)
        writer.writerows(data)


if __name__ == "__main__":
    run_as_main()