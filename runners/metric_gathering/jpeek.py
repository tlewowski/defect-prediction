import csv
import os
import subprocess
import xml.etree.ElementTree as ET

from metric_value import MetricValue
from project import Project
from iresearch_context import IResearchContext
from metrics_tool import MetricsTool


class JPeek(MetricsTool):
    name = 'jpeek'

    def __init__(self, jpeek_path: str, context: IResearchContext):
        self.jpeek_path = jpeek_path
        self.context = context

    def analyze(self, project: Project) -> str:
        if self.context.build:
            project.build()

        raw_results_dir = self.context.metrics_wd(self, project)

        if self.context.analyze:
            args = [
                self.context.binary_path("java"),
                "-jar",
                self.jpeek_path,
                "--sources",
                project.src_path,
                "--target",
                raw_results_dir
            ]
            print("JPEEK: running with:", args)
            subprocess.run(args)

        return raw_results_dir

    def normalize_results(self, raw_results: str, project: Project):
        metrics = ET.parse(os.path.join(raw_results, "index.xml")).findall("./metric")
        metric_names = [m.attrib.get("name") for m in metrics]
        print("JPEEK: extracting metrics:", metric_names, "for project:", project.name, "(", project.revision, ")")

        reports_path = self.context.reports_wd(self, project)
        all_metrics = []
        for metric in metric_names:
            name = "JPEEK_" + metric
            metric_file = ET.parse(os.path.join(raw_results, metric + ".xml"))
            metric_values = [MetricValue(name, c.attrib.get('id'), c.attrib.get('value')) for c in metric_file.findall("./app/class")]
            package_values = [
                MetricValue(name, p.attrib.get('id') + '.' + c.attrib.get('id'), c.attrib.get('value'))
                for p in metric_file.findall("./app/package")
                for c in p.findall('./class')
            ]
            all_metrics.extend(metric_values)
            all_metrics.extend(package_values)

        target_file = os.path.join(reports_path, "metrics.csv")
        self.print_final_metrics(target_file, all_metrics)
        print("JPEEK: Written", len(all_metrics), "metric values for", len(metric_names), "metrics to", target_file)
