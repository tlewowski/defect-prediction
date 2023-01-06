import datetime
import os
import subprocess
import time

import humanize
from build_tool import BuildTool
from iresearch_context import IResearchContext
from projects.mvn.overrides import CMD_OVERRIDES
from projects.maven_project import MavenProject

DEFAULT_MVN_CMD = [
    '-DskipTests',
    '-DfailIfNoTests=false',
    '-X',
    '-e',
    'compile'
]


class Maven(BuildTool):
    name = 'maven'

    def __init__(self, binary_path: str, research_context: IResearchContext):
        self.binary_path = binary_path
        self.context = research_context

    def build(self, project: MavenProject, local_repo: str):
        cmd = DEFAULT_MVN_CMD.copy()
        if project.name in CMD_OVERRIDES:
            cmd = CMD_OVERRIDES.get(project.name).copy()

        cmd.insert(0, '-Dmaven.repo.local=' + local_repo)
        cmd.insert(0, self.binary_path)

        maven_log = os.path.join(self.context.logs_dir(project), "maven.log")
        print("MVN: building", project.name, "with", cmd, "logs going to", maven_log)
        start_ts = time.monotonic()
        with open(maven_log, mode="w", encoding="utf-8") as log:
            proc = subprocess.run(cmd, cwd=project.src_path, stdout=log, stderr=log)
            if proc.returncode.real != 0:
                print("MVN: failed to build", project.name, "at", project.revision, ". Log at", maven_log)
                raise RuntimeError("Failed to build Maven project {} at {}. Log at {}".format(project.name, project.revision, maven_log))
        end_ts = time.monotonic()
        print("MVN: build of", project.name, "at", project.revision, "took:", humanize.naturaldelta(datetime.timedelta(seconds=end_ts-start_ts), minimum_unit="milliseconds"))
