import csv

from metric_gathering.metric_value import MetricValue
from metric_gathering.project import Project


class MetricsTool:
    name: str

    def analyze(self, project: Project) -> str:
        pass

    def normalize_results(self, raw_results_path: str, project: Project):
        pass

    def print_final_metrics(self, target_path: str, entries: list[MetricValue]):
        csv_header = ["metric_name", "entity", "metric_value"]
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
