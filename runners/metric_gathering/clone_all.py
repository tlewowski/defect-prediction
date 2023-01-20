#!/bin/env python

import os
import re
import argparse

from singlerun import single_run_with_args, single_run_parser


def clone_repo(workspace, line):
  elems = line.strip().split("\t")
  repo = elems[0]
  dir = re.findall("^.*/([a-zA-Z-_0-9.]*).git$", repo)[0]
  org_dir = os.path.join(workspace, re.findall("^.*:(.*)/.*\.git$", repo)[0])
  sha = elems[1]
  print("GITC: Cloning {} version {} to {}".format(repo, sha, dir))

  target = os.path.join(org_dir, dir)

  if not os.path.exists(org_dir):
    os.mkdir(org_dir)
  else:
    print("GITC: {} organization directory already exists, skipping creation".format(org_dir))

  if not os.path.exists(target):
    os.system("git clone " + repo + " " + target)
  else:
    print("GITC: {} repository already exists, skipping cloning".format(target))

  os.system("cd " + target + " && " + "git checkout " + sha + " && git clean -f -d -x")
  return target


def run_clone(args):
  with open(os.path.abspath(args.repos_file), 'r', encoding='utf-8') as f:
    lines = f.readlines()

    k = 0
    for line in lines:
      k = k + 1
      try:
        print("CLONER: Running project {} out of {}".format(k, len(lines)))
        project_path = clone_repo(os.path.abspath(args.clone_root), line)

        if args.run_pmd is not None:
          pmd_args = single_run_parser().parse_args(
            "--tool pmd --tool_path {} --project_path {} --wd_path {} --report_path {} --analyze --postprocess".format(
              os.path.join(args.run_pmd), project_path, os.path.join(args.calculation_wd), os.path.join(args.report_path)
            )
          )
          print("CLONER: Running PMD with args: {}".format(pmd_args))
          single_run_with_args(pmd_args, None)

        if args.run_javametrics is not None:
          javametrics_args = single_run_parser().parse_args(
            "--tool javametrics --tool_path {} --project_path {} --wd_path {} --report_path {} --analyze --postprocess".format(
              os.path.join(args.run_javametrics), project_path, os.path.join(args.calculation_wd), os.path.join(args.report_path)
            )
          )

          print("CLONER: Running JavaMetrics with args: {}".format(pmd_args))
          single_run_with_args(javametrics_args, None)


      except Exception as e:
        print("GITC: failed to clone repository {}: {}".format(line, e))

def clone_cli_parser():
  parser = argparse.ArgumentParser(description="Clone all repositories listed in a file into a JavaMetricsPP-compatible layout")
  parser.add_argument("--clone_root", type=str, help="directory into which all the repositories will be cloned", required=True)
  parser.add_argument("--repos_file", type=str, help="file with list of repositories and commits to clone. One line per repository. Github only. SSH link only. Single line per repository. Example line: >git@github.com:apache/cloudstack.git	8d3feb100aab4a45b31a789f444038b892161eec<", required=True)
  parser.add_argument("--run_pmd", type=str, help="PMD home location", required=False)
  parser.add_argument("--run_javametrics", type=str, help="JavaMetrics jar file location", required=False)
  parser.add_argument("--report_path", type=str, help="location of metrics reports", required=False)
  parser.add_argument("--calculation_wd", type=str, help="working directory for calculations", required=False)
  return parser
def run_as_main():
  args = clone_cli_parser().parse_args()
  run_clone(args)

if __name__ == '__main__':
  run_as_main()