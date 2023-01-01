import subprocess

from build_tool import BuildTool
from iresearch_context import IResearchContext
from projects.mvn.overrides import CMD_OVERRIDES
from projects.maven_project import MavenProject

DEFAULT_MVN_CMD = [
    '-DskipTests',
    '-DfailIfNoTests=false',
    'compile'
]


class Maven(BuildTool):
    name = 'maven'

    def __init__(self, binary_path: str, research_context: IResearchContext):
        self.binary_path = binary_path
        self.context = research_context

    def build(self, project: MavenProject, target_dir: str):
        cmd = DEFAULT_MVN_CMD.copy()
        if project.name in CMD_OVERRIDES:
            cmd = CMD_OVERRIDES.get(project.name).copy()

        cmd.insert(0, '-Dmaven.repo.local=' + self.context.build_tool_wd(self))
        cmd.insert(0, self.binary_path)

        print("MVN: building", project.name, "with", cmd)
        subprocess.run(cmd, cwd=project.src_path)
