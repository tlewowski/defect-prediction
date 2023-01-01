import argparse

from research_context import ResearchContext

def single_run_parser():
    parser = argparse.ArgumentParser(description="Calculate software project product metrics")
    parser.add_argument("--tool", type=str, help="name of the tool to use (pmd / jpeek / ckjm-ext)", required=True)
    parser.add_argument("--tool_path", type=str, help="path to the tool location", required=False)
    parser.add_argument("--project_path", type=str, help="path to the analyzed project", required=True)
    parser.add_argument("--report_path", type=str, help="path to the final output reports", required=True)
    parser.add_argument("--wd_path", type=str, help="path to the working directory", required=True)
    parser.add_argument("--build", action=argparse.BooleanOptionalAction, help="build the projects", default=False)
    parser.add_argument("--analyze", action=argparse.BooleanOptionalAction, help="analyze the projects", default=False)
    return parser

def single_run_with_args(args):
    print("MGMAIN_S: Starting analysis: {} on {}".format(args.tool, args.project_path))
    context = ResearchContext(args.report_path, args.wd_path, args)
    tool = context.metrics_tool(args.tool, args.tool_path)
    project = context.project(args.project_path)

    raw_results = tool.analyze(project)
    tool.normalize_results(raw_results, project)

    print("MGMAIN_S: Finished!")
def run_as_main():
    args = single_run_parser().parse_args()
    single_run_with_args(args)


if __name__ == '__main__':
    run_as_main()
