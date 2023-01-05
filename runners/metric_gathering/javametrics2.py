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
    with open(class_file, "r") as f:
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
class JavaMetrics2(MetricsTool):
    name = 'javametrics2'

    @staticmethod
    def make_entity_name(items: list[str]) -> str:
        assert len(items) == 5, "Expected 4 items, got: {}".format(items)
        return "-/+/-".join(items)

    @staticmethod
    def metrics_from_row(row: list[str], header: list[str]) -> list[MetricValue]:
        entity_name = JavaMetrics2.make_entity_name(row[0:5])
        values = row[5:]
        names = header[5:]
        pairs = zip(names, values)

        return [MetricValue("JAVAMETRICS_{}".format(p[0]), entity_name, p[1]) for p in pairs]


    def __init__(self, javametrics2_jar, context: IResearchContext):
        if javametrics2_jar is None or not os.path.isfile(javametrics2_jar):
            raise RuntimeError("JavaMetrics2 path not given or is not a file. Got: {}".format(javametrics2_jar))

        self.javametrics2_jar = javametrics2_jar
        self.context = context

    def make_sample_list(self, workspace: str, project: Project, only_paths: list[str]):
        filename = os.path.join(workspace, "javametrics2_samples.csv")
        repo_remote = Repo(project.src_path).remotes[0].url

        sample_id = 1
        with open(filename, "w") as f:
            f.write("SAMPLE_ID,TYPE,PACKAGE,OUTER_CLASS,CLASS,METHOD,PARAMETERS,REPOSITORY,COMMIT_HASH,GIT_SOURCE_FILE_URL,START_LINE,END_LINE,PATH\n")
            for class_file in only_paths:
                (package_name, class_name) = extract_class_name(class_file)
                if class_name != "":
                    sample_id = sample_id + 1

                    # this is weird, but it's how JavaMetrics 2 does it
                    relative_path = "/" + os.path.relpath(class_file, start=project.src_path)
                    f.write(f"{sample_id},class,{package_name},,{class_name},,,{repo_remote},{project.revision},,0,0,{relative_path}\n")

        if sample_id == 1:
            return None

        return filename
    def analyze(self, project: Project, only_paths: list[str] | None) -> str:
        raw_results_dir = self.context.metrics_wd(self, project)

        if self.context.analyze:
            args = [self.context.binary_path("java"), "-cp", self.javametrics2_jar, "main.Main"]
            args.extend(["-gitsources", os.path.join(project.src_path, "..", "..")])
            args.extend(["-workdir", os.path.join(self.context.workspace(self, project), "temporary")])
            if only_paths is None:
                raise RuntimeError("JavaMetrics2 support only change-based analysis")

            sample_list = self.make_sample_list(self.context.workspace(self, project), project, only_paths)
            if sample_list is None:
                print("JAVAMETRICS2: no inspectable change in", project.name, "at", project.revision, ". Skipping")
                return None

            args.extend(["-csv", sample_list])

            args.extend(["-outdir", raw_results_dir])

            javametrics2_log = os.path.join(self.context.logs_dir(project), "javametrics2.log")
            print("JAVAMETRICS2: running with:", args, "logs going to", javametrics2_log)
            with open(javametrics2_log, "w") as log:
                proc = subprocess.run(args, cwd=project.src_path, stdout=log, stderr=log)
                if proc.returncode.real != 0:
                    print("JAVAMETRICS2: failed to analyze", project.name, "at", project.revision, ". Log at", javametrics2_log)
                    raise RuntimeError(
                        "Failed to analyze project {} at {} with JavaMetrics2. Log at {}".format(project.name, project.revision, javametrics2_log))

        return os.path.join(raw_results_dir, "class_metrics.csv")


    def can_normalize(self, path: str) -> bool:
        return os.path.isfile(path)
    def normalize_results(self, raw_results_path: str, project: Project):
        all_metrics = []

        if not os.path.isfile(raw_results_path):
            print("JAVAMETRICS2: No results for", project.name, "at", project.revision, ". Skipping", raw_results_path)
            return

        with open(raw_results_path, 'r') as file:
            result_reader = csv.reader(file, delimiter = ",")
            headers = next(result_reader)
            for row in result_reader:
                all_metrics.extend(JavaMetrics2.metrics_from_row(row, headers))

        reports_path = self.context.reports_wd(self, project)
        target_file = os.path.join(reports_path, "metrics.csv")
        self.print_final_metrics(target_file, all_metrics)

        print("JAVAMETRICS2: Extracted", len(all_metrics), "metrics from", raw_results_path)
