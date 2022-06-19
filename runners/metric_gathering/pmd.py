import os
import subprocess
import xml.etree.ElementTree as ET

from iresearch_context import IResearchContext
from metric_gathering.metric_value import MetricValue
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
        self.pmd_home_path = pmd_home_path
        self.context = context

    def analyze(self, project: Project) -> str:
        target_dir = self.context.metrics_wd(self, project)
        target_file = os.path.join(target_dir, 'report.xml')
        pmd_cache = os.path.join(target_dir, 'cache')

        if self.context.analyze:
            cmd = pmd_runner().copy()
            cmd[0] = os.path.join(self.pmd_home_path, "bin", cmd[0])
            output_format = ['--format', 'xml', '--report-file', target_file]
            cmd.extend(['--dir', project.src_path, '--cache', pmd_cache])
            cmd.extend(output_format)
            cmd.extend(['--rulesets', os.path.join(RULESET_LOCATION, "java-ruleset.xml")])

            print("PMD: Running with", cmd)
            subprocess.run(cmd)

        return target_file

    def normalize_results(self, raw_results_path: str, project: Project):
        print("PMD: extracting metrics for project: ", project.name, "from", raw_results_path)

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
