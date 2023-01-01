import argparse
import os
import time

from git import InvalidGitRepositoryError
from gitdb.exc import BadName

from singlerun import single_run_parser
from git.repo.base import Repo


class InvalidGitCommitRange(Exception):
    def __init__(self, repo, start, end):
        self.repo = repo
        self.start = start
        self.end = end

def multirun_parser():
    parser = single_run_parser()
    parser.add_argument("--start", type=str, help="First commit to analyze", required=False)
    parser.add_argument("--end", type=str, help="Last commit to analyze", required=True)
    return parser

def first_commit(repo):
    pass

def validate_commit_range(repo, start, end):
    start_commit = None
    if start is not None:
        start_commit = repo.commit(start)

    end_commit = repo.commit(end)

    if start is not None and not repo.is_ancestor(start_commit, end_commit):
        raise InvalidGitCommitRange(repo, start, end)

    return [start_commit, end_commit]

def get_commit_iterator(repo, args):
    start = args.start
    end = args.end

    start_commit, end_commit = validate_commit_range(repo, start, end)

    if start_commit is not None:
        commits = list(repo.iter_commits(rev="{}..{}".format(start, end)))
        commits.append(start_commit)
    else:
        commits = list(repo.iter_commits(rev=end))

    return commits

def get_git_repo(path):
    return Repo(path=path)
def run_as_main():
    parser = multirun_parser()
    args = parser.parse_args()
    try:
        repo = get_git_repo(args.project_path)
        commits = get_commit_iterator(repo, args)
    except InvalidGitRepositoryError:
        print("MGMAIN_M: ", args.project_path, " (" + os.path.abspath(args.project_path) + ") is not a valid Git repository root. Exiting.")
        exit(1)
    except BadName as n:
        print("MGMAIN_M: Failed to find commit ", n.args[0], " in ", args.project_path, " (" + os.path.abspath(args.project_path) + ")")
        exit(1)
    except InvalidGitCommitRange as r:
        print("MGMAIN_M: Invalid commit range: from ", r.start, " to ", r.end, " in ", args.project_path, " (" + os.path.abspath(args.project_path) + ")")
        exit(1)

    total_commits = len(commits)
    print("MGMAIN_M: Got a total of " + str(total_commits) + " commits to analyze for ", args.project_path, " (" + os.path.abspath(args.project_path) + ")")
    current_index = 1
    start_time = time.monotonic()
    for commit in commits:
        commit_start_time = time.monotonic()
        print("MGMAIN_M: Checking out commit " + str(current_index) + "/" + str(total_commits) + " (" + commit.hexsha + ") in ", args.project_path, " (" + os.path.abspath(args.project_path) + ")")
        repo.head.reference = commit
        repo.head.reset(index=True, working_tree=True)
        commit_end_time = time.monotonic()
        time_taken = commit_end_time - commit_start_time
        total_time = commit_end_time - start_time
        avg_commit_time = total_time / current_index
        print("MGMAIN_M: Finished dealing with commit " + str(current_index) + "/" + str(
            total_commits) + " (" + commit.hexsha + ") in ", args.project_path,
              " (" + os.path.abspath(args.project_path) + "). Time taken: current: " + str(time_taken) + "s / total: " + str(total_time) + "s / average: " + str(avg_commit_time) + "s" )
        current_index = current_index + 1

if __name__ == '__main__':
    run_as_main()