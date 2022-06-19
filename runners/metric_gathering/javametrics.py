import os
import subprocess

from iresearch_context import IResearchContext
from metrics_tool import MetricsTool
from project import Project

class JavaMetrics(MetricsTool):
    name = 'javametrics'

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

    def normalize_results(self, raw_results_path: str, project: Project) -> str:
        pass
