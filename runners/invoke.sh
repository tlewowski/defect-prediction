#!/usr/bin/env sh

echo Remember to run in virtualenv that has required packages

# For JPeek
python metric_gathering/multirun.py --tool jpeek --build --analyze --tool_path L:\PhD\tools\jpeek\jpeek-0.31.1-jar-with-dependencies.jar --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\ignite --start fe445101265968109c5c4de82e635ec1700f58c4 --end 9464ca13212de5dbcc72c6e1f9e2805e72d8157a

# For PMD
python metric_gathering/multirun.py --tool pmd --analyze --tool_path L:\PhD\tools\pmd\pmd-bin-6.53.0 --wd_path L:\PhD\workspace --report_path L:\PhD\reports --project_path L:\PhD\repos\apache\ignite --start fe445101265968109c5c4de82e635ec1700f58c4 --end 9464ca13212de5dbcc72c6e1f9e2805e72d8157a
