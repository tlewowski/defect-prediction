import os
import subprocess
import csv

from iresearch_context import IResearchContext
from metric_value import MetricValue
from metrics_tool import MetricsTool
from project import Project

class JavaMetrics(MetricsTool):
    name = 'javametrics'

    @staticmethod
    def make_entity_name(items: list[str]) -> str:
        assert len(items) == 5, "Expected 4 items, got: {}".format(items)
        return "-/+/-".join(items)

    @staticmethod
    def metrics_from_row(row: list[str], header: list[str]) -> list[MetricValue]:
        entity_name = JavaMetrics.make_entity_name(row[0:5])
        values = row[5:]
        names = header[5:]
        pairs = zip(names, values)

        return [MetricValue("JAVAMETRICS_{}".format(p[0]), entity_name, p[1]) for p in pairs]


    def __init__(self, javametrics_jar, context: IResearchContext):
        self.javametrics_jar = javametrics_jar
        self.context = context

    def analyze(self, project: Project) -> str:
        raw_results_dir = self.context.metrics_wd(self, project)

        if self.context.analyze:
            args = [
                self.context.binary_path("java"),
                "-jar",
                self.javametrics_jar,
                "-i",
                project.src_path,
                "-o",
                raw_results_dir
            ]
            print("JAVAMETRICS: running with:", args)
            subprocess.run(args)

        return raw_results_dir

    def normalize_results(self, raw_results_path: str, project: Project):
        all_metrics = []
        with open(raw_results_path, 'r') as file:
            result_reader = csv.reader(file, delimiter = ",")
            headers = next(result_reader)
            for row in result_reader:
                all_metrics.extend(JavaMetrics.metrics_from_row(row, headers))

        reports_path = self.context.reports_wd(self, project)
        target_file = os.path.join(reports_path, "metrics.csv")
        self.print_final_metrics(target_file, all_metrics)

        print("JAVAMETRICS: Extracted", len(all_metrics), "metrics from", len(raw_results_path))
