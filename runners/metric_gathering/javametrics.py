import os
import re
import subprocess
import csv

from git import Repo

from iresearch_context import IResearchContext
from metric_value import MetricValue
from metrics_tool import MetricsTool
from project import Project

def extract_package(class_file):
    with open(class_file, mode="r", encoding="utf-8") as f:
        contents = f.read()
        found = re.search("package (.*);", contents)
        if not found is None:
            return found.group(1)
        else:
            return None
def extract_class_name(class_file):
    (_, filename) = os.path.split(class_file)
    (hopefully_class_name, extension) = os.path.splitext(filename)

    if extension != ".java":
        return "", ""

    package = extract_package(class_file)
    if package is None:
        return "", hopefully_class_name

    return package, hopefully_class_name

# Supported version is JavaMetrics Lite, not the full one
class JavaMetrics(MetricsTool):
    name = 'javametrics'

    @staticmethod
    def make_entity_name(items: list[str]) -> str:
        assert len(items) == 5, "Expected 5 items, got: {}".format(items)
        return ".".join([items[1], items[3]])

    @staticmethod
    def metrics_from_row(row: list[str], header: list[str]) -> list[MetricValue]:
        entity_name = JavaMetrics.make_entity_name(row[0:5])
        if row[4] != "":
            return []

        values = row[5:]
        names = header[5:]
        pairs = zip(names, values)

        return [MetricValue("JAVAMETRICS_{}".format(p[0]), entity_name, p[1]) for p in pairs]


    def __init__(self, javametrics_jar, context: IResearchContext):
        if javametrics_jar is None or not os.path.isfile(javametrics_jar):
            raise RuntimeError("JavaMetrics path not given or is not a file. Got: {}".format(javametrics_jar))

        self.javametrics_jar = javametrics_jar
        self.context = context

    def make_sample_list(self, workspace: str, project: Project, only_paths: list[str]):
        filename = os.path.join(workspace, "javametrics_sample_list.csv")

        sample_id = 1
        with open(filename, mode="w", encoding="utf-8") as f:
            f.write("file,package,class,method\n")
            for class_file in only_paths:
                (package_name, class_name) = extract_class_name(class_file)
                if class_name != "":
                    sample_id = sample_id + 1
                    f.write(f"{class_file},{package_name},{class_name},\n")

        if sample_id == 1:
            return None

        return filename

    def target_file(self, dir):
        return os.path.join(dir, "javametrics-out.csv")
    def analyze(self, project: Project, only_paths: list[str] | None) -> str:
        raw_results_dir = self.context.metrics_wd(self, project)

        if self.context.analyze:
            args = [self.context.binary_path("java"), "-jar", self.javametrics_jar]
            args.extend(["--input", project.src_path])

            if only_paths is not None:
                sample_list = self.make_sample_list(self.context.workspace(self, project), project, only_paths)
                if sample_list is None:
                    print("JAVAMETRICS: no inspectable change in", project.name, "at", project.revision, ". Skipping")
                    return None

                # according to JavaMetrics documentation -gitsources should point to the location of all repositories
                # at least if you want to download it. But if you do so, it gets crazy and starts parsing all the repos
                # each time, which is not exactly optimal, hence only project source
                args.extend(["--filter", sample_list])

            args.extend(["--output", self.target_file(raw_results_dir)])

            javametrics_log = os.path.join(self.context.logs_dir(project), "javametrics.log")
            print("JAVAMETRICS: running with:", args, "logs going to", javametrics_log)
            with open(javametrics_log, mode="w", encoding="utf-8") as log:
                proc = subprocess.run(args, cwd=project.src_path, stdout=log, stderr=log)
                if proc.returncode.real != 0:
                    print("JAVAMETRICS: failed to analyze", project.name, "at", project.revision, ". Log at", javametrics_log)
                    raise RuntimeError(
                        "Failed to analyze project {} at {} with JavaMetrics. Log at {}".format(project.name, project.revision, javametrics_log))

        return self.target_file(raw_results_dir)

    def can_normalize(self, path: str) -> bool:
        if not os.path.isfile(path):
            print("JAVAMETRICS: cannot normalize results from", path, "because it's not a file")
            return False
        return True

    def normalize_results(self, raw_results_path: str, project: Project):
        all_metrics = []
        with open(raw_results_path, mode='r', encoding="utf-8") as file:
            result_reader = csv.reader(file, delimiter=",")
            headers = next(result_reader)
            for row in result_reader:
                all_metrics.extend(JavaMetrics.metrics_from_row(row, headers))

        reports_path = self.context.reports_wd(self, project)
        target_file = os.path.join(reports_path, "metrics.csv")
        self.print_final_metrics(target_file, all_metrics)

        print("JAVAMETRICS: Extracted", len(all_metrics), "metrics from", raw_results_path, "final target:", target_file)
