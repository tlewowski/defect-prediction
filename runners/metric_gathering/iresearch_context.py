from argparse import Namespace

from build_tool import BuildTool
from project import Project
from metrics_tool import MetricsTool


class IResearchContext:
    build: bool
    analyze: bool
    params: Namespace

    def metrics_tool(self, tool_name: str, tool_path: str) -> MetricsTool:
        pass

    def build_tool(self, tool_name: str) -> BuildTool:
        pass

    def project(self, project_path: str) -> Project:
        pass

    def build_wd(self, project: Project) -> str:
        pass

    def logs_dir(self, project: Project) -> str:
        pass

    def metrics_wd(self, tool: MetricsTool, project: Project) -> str:
        pass

    def build_tool_wd(self, tool: BuildTool) -> str:
        pass

    def binary_path(self, name: str) -> str:
        pass

    def reports_wd(self, tool: MetricsTool, project: Project) -> str:
        pass