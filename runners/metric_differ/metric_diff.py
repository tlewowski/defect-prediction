import csv
import os


class MetricDiff:
    metric: str
    entity: str
    added: bool
    removed: bool
    change: any

    def __init__(self, metric: str, entity: str, added: bool = False, removed: bool = False, change: any = None):
        self.metric = metric
        self.entity = entity
        self.added = added
        self.removed = removed
        self.change = change

    def as_tuple(self):
        return self.metric, self.entity, self.added, self.removed, self.change

def save_diff(file: str, diff: list[MetricDiff]):
    csv_header = ["metric_name", "entity", "added", "removed", "value_change"]
    os.makedirs(file, exist_ok=True)
    target_path = os.path.join(file, "diff.csv")

    print("MDIFF: Saving", len(diff), "metric diffs to", target_path)
    with open(target_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        writer.writerows([e.as_tuple() for e in diff])
