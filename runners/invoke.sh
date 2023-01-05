#!/usr/bin/env sh

echo Remember to run in virtualenv that has required packages

# For JPeek
python metric_gathering/multirun.py --tool jpeek --build --analyze --tool_path L:\PhD\tools\jpeek\jpeek-0.31.1-jar-with-dependencies.jar --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\ignite --start fe445101265968109c5c4de82e635ec1700f58c4 --end 9464ca13212de5dbcc72c6e1f9e2805e72d8157a

# For PMD
python metric_gathering/multirun.py --tool pmd --analyze --tool_path L:\PhD\tools\pmd\pmd-bin-6.53.0 --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\ignite

# For JavaMetrics
python metric_gathering/multirun.py --tool javametrics --analyze --postprocess --tool_path L:\PhD\tools\javametrics\lite\java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\ignite --only_commits ../data/commits-ignite.txt --allow_no_metrics

python metric_gathering/multirun.py --tool javametrics2 --analyze --tool_path L:\PhD\tools\javametrics2\javametrics2.jar --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\ignite --start fe445101265968109c5c4de82e635ec1700f58c4 --end 9464ca13212de5dbcc72c6e1f9e2805e72d8157a


# PMD - gather whole Ignite
 L:\PhD\defect-prediction\runners>python metric_gathering/multirun.py --tool pmd --analyze --tool_path L:\PhD\tools\pmd\pmd-bin-6.53.0 --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\ignite --allow_no_metrics --max_failures 15000 --only_commits ..\data\commits-ignite.txt