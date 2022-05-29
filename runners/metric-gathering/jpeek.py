import os
import subprocess

from project import Project
from iresearch_context import IResearchContext
from metrics_tool import MetricsTool


class JPeek(MetricsTool):
    name = 'jpeek'

    def __init__(self, jpeek_path: str, context: IResearchContext):
        self.jpeek_path = jpeek_path
        self.context = context

    def analyze(self, project: Project):
        if self.context.no_build:
            project.build()

        args = [
            self.context.binary_path("java"),
            "-jar",
            self.jpeek_path,
            "--sources",
            project.src_path,
            "--target",
            self.context.metrics_wd(self, project)
        ]

        print(args)

        subprocess.run(args)