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
    with open(class_file, mode="r", encoding="utf-8",errors="ignore") as f:
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


class JavaMetrics2(MetricsTool):
    name = 'javametrics2'

    @staticmethod
    def metrics_from_row(class_lookup: dict[str, str], row: list[str], header: list[str]) -> list[MetricValue]:
        entity_name = class_lookup[row[0]]
        values = row[2:]
        names = header[2:]
        pairs = zip(names, values)

        return [MetricValue("JAVAMETRICS2_{}".format(p[0]), entity_name, p[1]) for p in pairs]


    def __init__(self, javametrics2_jar, context: IResearchContext):
        if javametrics2_jar is None or not os.path.isfile(javametrics2_jar):
            raise RuntimeError("JavaMetrics2 path not given or is not a file. Got: {}".format(javametrics2_jar))

        self.javametrics2_jar = javametrics2_jar
        self.context = context

    def make_sample_list(self, workspace: str, project: Project, only_paths: list[str]):
        filename = self.sample_names_location(workspace)
        repo_remote = Repo(project.src_path).remotes[0].url

        sample_id = 1
        with open(filename, mode="w", encoding="utf-8") as f:
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

    def sample_names_location(self, dir: str) -> str:
        return os.path.join(dir, "javametrics2_samples.csv")
    def class_metrics_location(self, raw_results_dir: str) -> str:
        return os.path.join(raw_results_dir, "class_metrics.csv")


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
            with open(javametrics2_log, mode="w", encoding="utf-8") as log:
                proc = subprocess.run(args, cwd=project.src_path, stdout=log, stderr=log)
                if proc.returncode.real != 0:
                    print("JAVAMETRICS2: failed to analyze", project.name, "at", project.revision, ". Log at", javametrics2_log)
                    raise RuntimeError(
                        "Failed to analyze project {} at {} with JavaMetrics2. Log at {}".format(project.name, project.revision, javametrics2_log))

        return self.class_metrics_location(raw_results_dir)


    def can_normalize(self, path: str) -> bool:
        if not os.path.isfile(path):
            print("JAVAMETRICS2: cannot normalize results from", path, "because it's not a file")
            return False
        return True

    def normalize_results(self, raw_results_path: str, project: Project):
        all_metrics = []

        if not os.path.isfile(raw_results_path):
            print("JAVAMETRICS2: No results for", project.name, "at", project.revision, ". Skipping", raw_results_path)
            return

        sample_names_file = self.sample_names_location(self.context.workspace(self, project))
        if not os.path.isfile(sample_names_file):
            print("JAVAMETRICS2: No sample names for", project.name, "at", project.revision, ". Path:", sample_names_file)

        class_lookup = {}
        with open(sample_names_file, mode="r", encoding="utf-8") as f:
            result_reader = csv.reader(f, delimiter=",")
            headers = next(result_reader)
            for row in result_reader:
                class_lookup[row[0]] = ".".join([row[2], row[4]])

        with open(raw_results_path, mode='r', encoding="utf-8") as file:
            result_reader = csv.reader(file, delimiter=",")
            headers = next(result_reader)
            for row in result_reader:
                all_metrics.extend(JavaMetrics2.metrics_from_row(class_lookup, row, headers))

        reports_path = self.context.reports_wd(self, project)
        target_file = os.path.join(reports_path, "metrics.csv")
        self.print_final_metrics(target_file, all_metrics)

        print("JAVAMETRICS2: Extracted", len(all_metrics), "metrics from", raw_results_path, "final target:", target_file)
