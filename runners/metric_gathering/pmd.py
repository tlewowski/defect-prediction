import os
import subprocess
import xml.etree.ElementTree as ET

from iresearch_context import IResearchContext
from metric_value import MetricValue
from metrics_tool import MetricsTool
from project import Project

RULESET_LOCATION = os.path.join(os.path.dirname(__file__), "..", "helpers", "pmd")
PMD_NS= {
    'pmdns': 'http://pmd.sourceforge.net/report/2.0.0'
}

def pmd_runner():
    if os.name == 'nt':
        return ['pmd.bat']
    else:
        return ['run.sh', 'pmd']

class PMD(MetricsTool):
    name = 'pmd'

    def __init__(self, pmd_home_path, context: IResearchContext):
        if pmd_home_path is None or not os.path.isdir(pmd_home_path):
            raise RuntimeError("PMD path not given or is not a file. Got: {}".format(pmd_home_path))

        self.pmd_home_path = pmd_home_path
        self.context = context

    def make_file_list(self, target_dir: str, only_paths: list[str]):
        filename = os.path.join(target_dir, "pmd_analyze_list.txt")
        with open(filename, mode="w", encoding="utf-8") as f:
            for line in only_paths:
                f.write(f"{line}\n")
        return filename
    def analyze(self, project: Project, only_paths: list[str] | None) -> str:
        target_dir = self.context.metrics_wd(self, project)
        target_file = os.path.join(target_dir, 'report.xml')
        pmd_cache = os.path.join(self.context.cache_dir(self, project), 'pmd.cache')

        if self.context.analyze:
            cmd = pmd_runner().copy()
            cmd[0] = os.path.join(self.pmd_home_path, "bin", cmd[0])
            output_format = ['--format', 'xml', '--report-file', target_file]
            if only_paths is not None:
                file_list = self.make_file_list(self.context.workspace(self, project), only_paths)
                cmd.extend(["--file-list", file_list])
            else:
                cmd.extend(['--dir', project.src_path])
                
            cmd.extend(['--cache', pmd_cache])
            cmd.extend(output_format)
            cmd.extend(['--rulesets', os.path.join(RULESET_LOCATION, "java-ruleset.xml")])
            cmd.extend(['--fail-on-violation', 'false'])

            pmd_log = os.path.join(self.context.logs_dir(project), "pmd.log")
            print("PMD: running with:", cmd, "logs going to", pmd_log)
            with open(pmd_log, mode="w", encoding="utf-8") as log:
                proc = subprocess.run(cmd,cwd=project.src_path, stdout=log, stderr=log)
                if proc.returncode.real != 0:
                    print("PMD: failed to analyze", project.name, "at", project.revision, ". Log at", pmd_log)
                    raise RuntimeError(
                        "Failed to analyze project {} at {} with PMD. Log at {}".format(project.name, project.revision, pmd_log))

        return target_file

    def can_normalize(self, path: str) -> bool:
        return os.path.isfile(path)
    def normalize_results(self, raw_results_path: str, project: Project):
        print("PMD: extracting metrics for project: ", project.name, "from", raw_results_path)
        if not os.path.isfile(raw_results_path):
            raise RuntimeError("Expected raw PMD results file at {}, but none found".format(raw_results_path))

        results = ET.parse(raw_results_path)
        files = results.findall('./pmdns:file', namespaces=PMD_NS)
        all_metrics = []

        for f in files:
            for v in f.findall('./pmdns:violation', namespaces=PMD_NS):
                pieces = v.text.split(":")
                metric_name = "PMD_" + pieces[0].strip()
                metric_value = float(pieces[1].strip())

                entity_name: str
                if "package" in v.attrib.keys():
                    entity_name = v.attrib.get("package") + "." + v.attrib.get("class")
                else:
                    entity_name = v.attrib.get("class")

                if "method" in v.attrib.keys():
                    entity_name = entity_name + "$" + v.attrib.get("method")

                all_metrics.append(MetricValue(metric_name, entity_name, metric_value))

        reports_path = self.context.reports_wd(self, project)
        target_file = os.path.join(reports_path, "metrics.csv")
        self.print_final_metrics(target_file, all_metrics)

        print("PMD: Extracted", len(all_metrics), "metrics from", len(files), "files (", results.getroot().tag, ")")
