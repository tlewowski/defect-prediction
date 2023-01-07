#!/usr/bin/env sh

echo Remember to run in virtualenv that has required packages

# For JPeek
python metric_gathering/multirun.py --tool jpeek --build --analyze --tool_path L:\PhD\tools\jpeek\jpeek-0.31.1-jar-with-dependencies.jar --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\ignite --start fe445101265968109c5c4de82e635ec1700f58c4 --end 9464ca13212de5dbcc72c6e1f9e2805e72d8157a

# For PMD
python metric_gathering/multirun.py --tool pmd --analyze --tool_path L:\PhD\tools\pmd\pmd-bin-6.53.0 --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\ignite



# Data gathering templates

# For JavaMetrics
python metric_gathering/multirun.py --tool javametrics --analyze --postprocess --tool_path L:\PhD\tools\javametrics\lite\java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\flink --only_commits ../data/commits/flink.txt --allow_no_metrics

# For JavaMetricsPP
python metric_gathering/multirun.py --tool javametrics2 --analyze --tool_path L:\PhD\tools\javametrics2\javametrics2.jar --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\groovy --allow_no_metrics --max_failures 15000 --only_commits ../data/commits/groovy.txt

# PMD - gather whole Ignite
python python metric_gathering/multirun.py --tool pmd --analyze --postprocess --tool_path L:\PhD\tools\pmd\pmd-bin-6.53.0 --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\ignite --allow_no_metrics --max_failures 15000 --only_commits ../data/commits/ignite.txt


# Collecting metrics for single tool
python metric_joining/project_joiner.py --metrics_root L:/PhD/reports/metrics/pmd --target_file L:/PhD/reports/metrics/pmd/complete.csv

# Collecting metrics from multiple tools
python metric_joining/tool_joiner.py --input L:/PhD/reports/metrics/pmd/complete.csv L:/PhD/reports/metrics/javametrics/complete.csv --join_on project revision entity --target_file L:/PhD/reports/metrics/all.csv