import csv

from metric_value import MetricValue
from project import Project


class MetricsTool:
    name: str

    def analyze(self, project: Project) -> str:
        pass

    def normalize_results(self, raw_results_path: str, project: Project) -> str:
        pass

    def print_final_metrics(self, target_path: str, entries: list[MetricValue]):
        csv_header = ["metric_name", "entity", "metric_value"]
        entries.sort(key=lambda e: e.entity)

        with open(target_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(csv_header)
            writer.writerows([e.as_tuple() for e in entries])
