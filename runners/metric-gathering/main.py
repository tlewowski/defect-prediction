# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import argparse

from research_context import ResearchContext

def run_as_main():
    parser = argparse.ArgumentParser(description="Calculate software project product metrics")
    parser.add_argument("--tool", type=str, help="name of the tool to use (pmd / jpeek / ckjm-ext)", required = True)
    parser.add_argument("--tool_path", type=str, help="path to the tool location", required = True)
    parser.add_argument("--project_path", type=str, help="path to the analyzed project", required = True)
    parser.add_argument("--report_path", type=str, help="path to the final output reports", required = True)
    parser.add_argument("--wd_path", type=str, help="path to the working directory", required = True)
    parser.add_argument("--no_build", type=bool, help="do not build the projects", default=False)

    args = parser.parse_args()

    context = ResearchContext(args.report_path, args.wd_path, args.no_build, args)
    tool = context.metrics_tool(args.tool, args.tool_path)
    project = context.project(args.project_path)

    tool.analyze(project)

    print(args)






# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_as_main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
