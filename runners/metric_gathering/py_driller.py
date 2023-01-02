import csv
import datetime
import functools
import os

from iresearch_context import IResearchContext
from metric_value import MetricValue
from metrics_tool import MetricsTool
from project import Project
from pydriller.metrics.process.contributors_count import ContributorsCount
from pydriller.metrics.process.hunks_count import HunksCount
from pydriller.metrics.process.lines_count import LinesCount
from pydriller.metrics.process.commits_count import CommitsCount
from pydriller.metrics.process.code_churn import CodeChurn
from pydriller.metrics.process.contributors_experience import ContributorsExperience
from pydriller.metrics.process.history_complexity import HistoryComplexity

METRICS = [
    ("ContributorsCount", ContributorsCount, ("count", "count_minor"), lambda x: (x.count(), x.count_minor())),
    ("HunksCount", HunksCount, ("count",), lambda x: (x.count(),)),
    ("LinesCount", LinesCount, ("count_added", "max_added", "avg_added", "count_removed", "max_removed", "avg_removed"), lambda x: (x.count_added(), x.max_added(), x.avg_added(), x.count_removed(), x.max_removed(), x.avg_removed())),
    ("CommitsCount", CommitsCount, ("count",), lambda x: (x.count(),)),
    ("CodeChurn", CodeChurn, ("count","max","avg"), lambda x: (x.count(), x.max(), x.avg())),
    ("ContributorsExperience", ContributorsExperience, ("count",), lambda x: (x.count(),)),
    ("HistoryComplexity", HistoryComplexity, ("count",), lambda x: (x.count(),))
]

class PyDriller(MetricsTool):
    name = 'pydriller'

    def __init__(self, context: IResearchContext):
        self.context = context

    def analyze(self, project: Project) -> str:
        target_dir = self.context.metrics_wd(self, project)

        if self.context.analyze:
            print("PYDRILL: Starting analysis. This may take a while!")

            for (name, calculator, columns, extractor) in METRICS:
                print("PYDRILL: Starting to analyze", name, "for", project.name)
                result = calculator(project.src_path, since=datetime.datetime.min, to=datetime.datetime.max)
                output = extractor(result)

                target_file = os.path.join(target_dir, name + ".csv")
                print("PYDRILL: Calculated", name, "for", project.name, "saving data to", target_file)
                with(open(target_file, "w") as f):
                    writer = csv.writer(f)
                    allcols = ["{0}_{1}".format(name, c) for c in columns]
                    allcols.append("file")
                    writer.writerow(allcols)

                    allentities = functools.reduce(lambda all, next: all | next, [col.keys() for col in output], set())
                    for entity in allentities:
                        vals = [c[entity] for c in output]
                        vals.append(entity)
                        writer.writerow(vals)

        return target_dir

    def normalize_results(self, raw_results_path: str, project: Project):
        reports_path = self.context.reports_wd(self, project)
        allfiles = [csvfile for csvfile in os.listdir(raw_results_path) if csvfile.endswith(".csv")]
        print("PYDRILL: Normalizing results from", raw_results_path, "(", len(allfiles), "files ), saving to", reports_path)
        all_metrics = []
        for file in allfiles:
            with(open(os.path.join(raw_results_path, file))) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    entity = row["file"]
                    others = [k for k in row.keys() if k != "file"]
                    for metric in others:
                        all_metrics.append(MetricValue(metric, entity, row[metric]))

        target_file = os.path.join(reports_path, "metrics.csv")
        self.print_final_metrics(target_file, all_metrics)
        print("PYDRILL: Saved", len(all_metrics), "metric values to", target_file)




