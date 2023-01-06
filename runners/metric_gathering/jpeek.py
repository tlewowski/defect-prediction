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
        if jpeek_path is None or not os.path.isfile(jpeek_path):
            raise RuntimeError("JPeek path not given or is not a file. Got: {}".format(jpeek_path))

        self.jpeek_path = jpeek_path
        self.context = context

    def analyze(self, project: Project, only_paths: list[str] | None) -> str:
        if only_paths is not None:
            raise RuntimeError("JPeek does not support incremental analysis (--only_paths flag is not allowed for jpeek)")

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
                raw_results_dir,
                "--overwrite",
                "--metrics",
                "C3,CAMC,CCM,LCC,LCOM,LCOM2,LCOM3,LCOM4,LCOM5,LORM,MMAC,MWE,NHD,OCC,PCC,SCOM,TCC,TLCOM"
            ]

            jpeek_log = os.path.join(self.context.logs_dir(project), "jpeek.log")
            print("JPEEK: running with:", args, "logs going to", jpeek_log)
            with open(jpeek_log, mode="w", encoding="utf-8") as log:
                proc = subprocess.run(args, cwd=project.src_path, stdout=log, stderr=log)
                if proc.returncode.real != 0:
                    print("JPEEK: failed to analyze", project.name, "at", project.revision, ". Log at", jpeek_log)
                    raise RuntimeError(
                        "Failed to analyze project {} at {} with JPeek. Log at {}".format(project.name, project.revision, jpeek_log))

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
