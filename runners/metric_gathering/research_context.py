from argparse import Namespace

from build_tool import BuildTool
from exec_resolver import resolve_full_path
from iresearch_context import IResearchContext
from jpeek import JPeek

import os

from javametrics import JavaMetrics
from py_driller import PyDriller
from pmd import PMD
from project import Project
from project_resolver import resolve_project
from metrics_tool import MetricsTool
from projects.maven import Maven
from javametrics2 import JavaMetrics2


class ResearchContext(IResearchContext):
    def __init__(self, report_directory: str, working_directory: str, params: Namespace):
        self.report_directory = report_directory
        self.working_directory = working_directory
        self.build = params.build
        self.analyze = params.analyze
        self.params = params

    def metrics_tool(self, tool_name, tool_path):
        if tool_name == 'jpeek':
            return JPeek(tool_path, self)
        elif tool_name == 'pmd':
            return PMD(tool_path, self)
        elif tool_name == 'javametrics':
            return JavaMetrics(tool_path, self)
        elif tool_name == 'javametrics2':
            return JavaMetrics2(tool_path, self)
        elif tool_name == 'pydriller':
            return PyDriller(self)
        else:
            raise RuntimeError("Unsupported tool!")

    def build_tool(self, tool_name: str) -> BuildTool:
        if tool_name == 'maven':
            return Maven(self.binary_path('mvn'), self)

    def binary_path(self, name: str) -> str:
        return resolve_full_path(name)

    def project(self, project_path) -> Project:
        return resolve_project(project_path, self)

    def metrics_wd(self, tool: MetricsTool, project: Project) -> str:
        return self.existing_directory(os.path.join(self.working_directory, "metrics", tool.name, project.name, project.revision))

    def reports_wd(self, tool: MetricsTool, project: Project) -> str:
        return self.existing_directory(os.path.join(self.report_directory, "metrics", tool.name, project.name, project.revision))

    def logs_dir(self, project: Project) -> str:
        return self.existing_directory(os.path.join(self.working_directory, "logs", project.name, project.revision))

    def cache_dir(self, tool: MetricsTool, project: Project) -> str:
        return self.existing_directory(os.path.join(self.working_directory, "cache", project.name, tool.name))

    def build_wd(self, project: Project) -> str:
        return self.existing_directory(os.path.join(self.working_directory, "build", project.name))

    def global_cache_dir(self, tool: BuildTool) -> str:
        return self.existing_directory(os.path.join(self.working_directory, "global-cache", tool.name))

    def workspace(self, tool: MetricsTool, project: Project) -> str:
        return self.existing_directory(os.path.join(self.working_directory, "workspace", tool.name, project.name, project.revision))
    def build_tool_wd(self, tool: BuildTool) -> str:
        return self.existing_directory(os.path.join(self.working_directory, "tool-stuff", tool.name))

    def existing_directory(self, path: str) -> str:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        return path


