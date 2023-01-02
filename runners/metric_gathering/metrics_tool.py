import csv

from metric_value import MetricValue
from project import Project


def as_matrix(metrics: list[MetricValue]):
    all_metrics = {}
    metric_names = {}
    header = ["entity"]
    for metric in metrics:
        if metric.metric not in metric_names:
            metric_names[metric.metric] = len(metric_names.keys()) + 1
            header.append(metric.metric)

        if metric.entity not in all_metrics:
            all_metrics[metric.entity] = {}

        all_metrics[metric.entity][metric.metric] = metric.value

    print("METRICS_TOOL: Got the following metrics:", metric_names.keys())
    matrix = []
    for entity in all_metrics.keys():
        entry = [None] * (len(metric_names.keys()) + 1)
        entry[0] = entity
        for metric in metric_names.keys():
            if metric in all_metrics[entity]:
                entry[metric_names[metric]] = all_metrics[entity][metric]

        matrix.append(entry)

    return header, matrix


class MetricsTool:
    name: str
    def analyze(self, project: Project, only_paths: list[str] | None) -> str:
        pass

    def normalize_results(self, raw_results_path: str, project: Project):
        pass


    def print_final_metrics(self, target_path: str, entries: list[MetricValue]):
        header, metrics = as_matrix(entries)
        metrics.sort(key=lambda e: e[0])

        with open(target_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(metrics)


def read_metrics_file(file: str) -> list[MetricValue]:
    metrics = []
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=',')

        next(reader) # skip header
        for row in reader:
            if len(row) > 0: # skip empty lines
                metrics.append(MetricValue(row[0], row[1], row[2]))

    return metrics
