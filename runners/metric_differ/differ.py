import os

from metric_differ.metric_diff import MetricDiff
from metric_gathering.metrics_tool import read_metrics_file


def diff_metrics(metrics_dir: str, later_commit: str, earlier_commit: str):
    newfile = read_metrics_file(os.path.join(metrics_dir, later_commit, 'metrics.csv'))
    oldfile = read_metrics_file(os.path.join(metrics_dir, earlier_commit, 'metrics.csv'))

    print("MDIFF: Diffing between", len(newfile), "metrics in new file and", len(oldfile), "metrics in the old file")

    # metrics files are sorted
    changes: list[MetricDiff] = []
    i = 0
    j = 0
    while i < len(newfile) or j < len(oldfile):
        n = newfile[i]
        o = oldfile[j]
        if o is None and n is None:
            break

        if n is None and not o is None:
            changes.append(MetricDiff(o.metric, o.entity, removed=True))
            j = j+1
        elif not n is None and o is None:
            changes.append(MetricDiff(n.metric, n.entity, added=True))
            i = i+1
        elif n.entity < o.entity or (n.entity == o.entity and n.metric < o.metric):
            changes.append(MetricDiff(n.metric, n.entity, added=True))
            i = i+1
        elif n.entity > o.entity or (n.entity == o.entity and n.metric > o.metric):
            changes.append(MetricDiff(o.metric, o.entity, removed=True))
            j = j+1
        else: # support only numeric values for now
            changes.append(MetricDiff(n.metric, n.entity, change=float(n.value)-float(o.value)))
            i = i+1
            j = j+1

    return changes