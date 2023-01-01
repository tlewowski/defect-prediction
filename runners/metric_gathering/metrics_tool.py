import csv

from metric_value import MetricValue
from project import Project


def as_matrix(metrics: list[MetricValue]):
    all_metrics = {}
    metric_names = {}
    for metric in metrics:
        metric_names[metric.metric] = True
        if metric.entity not in all_metrics:
            all_metrics[metric.entity] = {}

        all_metrics[metric.entity][metric.metric] = metric.value





class MetricsTool:
    name: str
    def analyze(self, project: Project) -> str:
        pass

    def normalize_results(self, raw_results_path: str, project: Project):
        pass


    def print_final_metrics(self, target_path: str, entries: list[MetricValue]):
        csv_header = ["metric_name", "entity", "metric_value"]
        metric_dict = as_matrix(entries)
        entries.sort(key=lambda e: e.entity + e.metric)

        with open(target_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(csv_header)
            writer.writerows([e.as_tuple() for e in entries])


def read_metrics_file(file: str) -> list[MetricValue]:
    metrics = []
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=',')

        next(reader) # skip header
        for row in reader:
            if len(row) > 0: # skip empty lines
                metrics.append(MetricValue(row[0], row[1], row[2]))

    return metrics
