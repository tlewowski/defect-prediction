import argparse
import datetime
import time

import humanize.time

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
    parser.add_argument("--postprocess", action=argparse.BooleanOptionalAction, help="run project postprocessing", default=False)
    parser.add_argument("--allow_no_metrics", action=argparse.BooleanOptionalAction, help="do not exit with failure if no metrics were calculated", default=False)
    return parser

def single_run_with_args(args, only_paths):
    print("MGMAIN_S: Starting analysis: {} on {} (subset: {})".format(args.tool, args.project_path, only_paths is not None))
    context = ResearchContext(args.report_path, args.wd_path, args)
    tool = context.metrics_tool(args.tool, args.tool_path)
    project = context.project(args.project_path)

    start_time = time.monotonic()
    raw_results = tool.analyze(project, only_paths)
    after_analysis = time.monotonic()
    print("MGMAIN_S: Analysis finished. Time taken:", humanize.naturaldelta(datetime.timedelta(seconds=after_analysis - start_time), minimum_unit="milliseconds"))
    if args.postprocess:
        if raw_results is None:
            if not args.allow_no_metrics:
                print("MGMAIN_S: No metrics calculated, but no --allow_no_metrics not set. Terminating with failure")
                raise RuntimeError("No metrics calculated, but no --allow_no_metrics not set. Terminating with failure")

            return

        tool.normalize_results(raw_results, project)

    after_normalization = time.monotonic()

    print("MGMAIN_S: Postprocessing of", args.project_path, " finished. Time taken - total: ",
          humanize.naturaldelta(datetime.timedelta(seconds=after_normalization - start_time), minimum_unit="milliseconds"),
          ", postprocessing:", humanize.naturaldelta(datetime.timedelta(seconds=after_normalization - after_analysis), minimum_unit="milliseconds"))

def run_as_main():
    args = single_run_parser().parse_args()
    single_run_with_args(args)


if __name__ == '__main__':
    run_as_main()
