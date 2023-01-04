import argparse
import datetime
import os
import time
import traceback

import humanize
from git import InvalidGitRepositoryError
from gitdb.exc import BadName

from singlerun import single_run_parser,single_run_with_args
from git.repo.base import Repo


class InvalidGitCommitRange(Exception):
    def __init__(self, repo, start, end):
        self.repo = repo
        self.start = start
        self.end = end

def multirun_parser():
    parser = single_run_parser()
    parser.add_argument("--max_failures", type=int, help="Number of errors that will not stop the analysis", default=0)
    parser.add_argument("--only_changes", type=bool, help="Only gather metrics for changed files", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--dry_run", type=bool, help="Do not run analysis, only verify validity of Git parameters", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--start", type=str, help="First commit to analyze. Ignored if --only_commits is given", required=False)

    commit_range = parser.add_mutually_exclusive_group(required=True)
    commit_range.add_argument("--end", type=str, help="Last commit to analyze. Either this parameter or --only_commits must be given")
    commit_range.add_argument("--only_commits", type=str, help="Path to a file that contains a list of commits (one per line) on which the analysis shall be executed. Either this parameter of --end must be given")
    return parser

def validate_commit_range(repo, start, end):
    start_commit = None
    if start is not None:
        start_commit = repo.commit(start)

    end_commit = repo.commit(end)

    if start is not None and not repo.is_ancestor(start_commit, end_commit):
        raise InvalidGitCommitRange(repo, start, end)

    return [start_commit, end_commit]

def get_commit_list(repo, args):
    if args.only_commits is not None:
        if not os.path.isfile(args.only_commits):
            raise RuntimeError("{} (--only_commits argument) should be a file containing commit SHA per line, but no such file found".format(args.only_commits))

        try:
            with open(args.only_commits) as f:
                candidates = f.readlines()
                return [repo.commit(c.strip()) for c in candidates]
        except Exception as ex:
            raise RuntimeError("{} (--only_commits argument) should be a file containing commit SHA per line. File found, but got an error during processing:{}".format(args.only_commits, ex))

    start = args.start
    end = args.end

    start_commit, end_commit = validate_commit_range(repo, start, end)

    if start_commit is not None:
        commits = list(repo.iter_commits(rev="{}..{}".format(start, end)))
        commits.append(start_commit)
    else:
        commits = list(repo.iter_commits(rev=end))

    commits.reverse()
    return commits

def get_git_repo(path):
    return Repo(path=path)


def project_tostring(project_path):
    absolute = os.path.abspath(project_path)
    if project_path != absolute:
        return "in {} ({})".format(project_path, absolute)

    return "in {}".format(project_path)

def touched_files(commit, project_path):
    if len(commit.parents) == 0:
        return [os.path.join(project_path, t.name) for t in commit.tree]

    return [os.path.join(project_path, d.a_path) for d in commit.diff(commit.parents[0])]
def run_as_main():
    parser = multirun_parser()
    args = parser.parse_args()
    try:
        repo = get_git_repo(args.project_path)
        commits = get_commit_list(repo, args)
    except InvalidGitRepositoryError as err:
        print("MGMAIN_M:", args.project_path, "(" + os.path.abspath(args.project_path) + ") is not a valid Git repository root. Exiting.")
        traceback.print_exception(err)
        exit(1)
    except BadName as n:
        print("MGMAIN_M: Failed to find commit", n.args[0], project_tostring(args.project_path))
        traceback.print_exception(n)
        exit(1)
    except InvalidGitCommitRange as r:
        print("MGMAIN_M: Invalid commit range: from", r.start, "to", r.end, project_tostring(args.project_path))
        traceback.print_exception(r)
        exit(1)

    total_commits = len(commits)
    print("MGMAIN_M: Got a total of", str(total_commits), "commits to analyze", project_tostring(args.project_path))
    current_index = 1
    successful = 0
    failed = 0
    start_time = time.monotonic()
    for commit in commits:
        commit_start_time = time.monotonic()
        print("MGMAIN_M: Checking out commit", str(current_index)+ "/" + str(total_commits), " (" + commit.hexsha + ")", project_tostring(args.project_path))
        try:
            repo.head.reference = commit
            repo.head.reset(index=True, working_tree=True)
        except Exception as ex:
            failed = failed + 1
            print("MGMAIN_M: Failed to checkout", commit.hexsha, project_tostring(args.project_path), "continuing with the next one.",
                  "Total failures:", str(failed), "Exception:", ex)
            traceback.print_exception(ex)
            current_index = current_index + 1
            if failed > args.max_failures:
                print("MGMAIN_M: Error threshold exceeded. Terminating.")
                exit(1)

            continue

        try:
            modifications = None
            if args.only_changes:
                modifications = touched_files(commit, args.project_path)

            if not args.only_changes or len(modifications) > 0:
                if not args.dry_run:
                    single_run_with_args(args, modifications)
                else:
                    print("MGMAIN_M: Skipping valid commit", commit.hexsha, project_tostring(args.project_path), "because of --dry_run param")
            else:
                print("MGMAIN_M: Skipping", commit.hexsha, project_tostring(args.project_path), "because no relevant change was found")
        except Exception as ex:
            failed = failed + 1
            print("MGMAIN_M: Failed to analyze", commit.hexsha, project_tostring(args.project_path), "continuing with the next one.",
                  "Total failures:", str(failed), "Exception:", ex)
            traceback.print_exception(ex)
            current_index = current_index + 1
            if failed > args.max_failures:
                print("MGMAIN_M: Error threshold exceeded. Terminating.")
                exit(1)

            continue

        commit_end_time = time.monotonic()
        time_taken = commit_end_time - commit_start_time
        total_time = commit_end_time - start_time
        avg_commit_time = total_time / current_index
        successful = successful + 1
        print("MGMAIN_M: Finished dealing with commit", str(current_index) + "/" + str(total_commits), "(" + commit.hexsha + ")", project_tostring(args.project_path) + ".",
              "Time taken - last:", humanize.naturaldelta(datetime.timedelta(seconds=time_taken), minimum_unit="milliseconds"),
              "/ total:",  humanize.naturaldelta(datetime.timedelta(seconds=total_time), minimum_unit="milliseconds"),
              "/ average:", humanize.naturaldelta(datetime.timedelta(seconds=avg_commit_time), minimum_unit="milliseconds") +
              ". Successful:", str(successful), "failures:", str(failed))
        current_index = current_index + 1

    print("MGMAIN_M: Finished analyzing the project", project_tostring(args.project_path))
    if failed != 0:
        print("MGMAIN_M: Encountered failures during processing. Please review the analysis log for details")

if __name__ == '__main__':
    run_as_main()