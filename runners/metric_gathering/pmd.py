import os
import subprocess

from iresearch_context import IResearchContext
from metrics_tool import MetricsTool
from project import Project

def pmd_runner():
    if os.name == 'nt':
        return ['pmd.bat']
    else:
        return ['run.sh', 'pmd']

class PMD(MetricsTool):
    name = 'pmd'

    def __init__(self, pmd_home_path, context: IResearchContext):
        self.pmd_home_path = pmd_home_path
        self.context = context

    def analyze(self, project: Project) -> str:
        target_dir = self.context.metrics_wd(self, project)
        target_file = os.path.join(target_dir, 'report.xml')
        pmd_cache = os.path.join(target_dir, 'cache')

        cmd = pmd_runner().copy()
        cmd[0] = os.path.join(self.pmd_home_path, "bin", cmd[0])
        output_format = ['--format', 'xml', '--report-file', target_file]
        cmd.extend(['--dir', project.src_path, '--cache', pmd_cache])
        cmd.extend(output_format)
        cmd.extend(['--rulesets', 'rulesets/java/quickstart.xml'])

        print("PMD: Running with", cmd)
        subprocess.run(cmd)

        return target_file

    def normalize_results(self, raw_results_path: str, project: Project) -> str:
        pass
