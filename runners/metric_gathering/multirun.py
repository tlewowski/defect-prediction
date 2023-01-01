import argparse
import os

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
    start_commit = repo.commit(start)
    end_commit = repo.commit(end)

    if not repo.is_ancestor(start_commit, end_commit):
        raise InvalidGitCommitRange(repo, start, end)

    return [start_commit, end_commit]

def get_commit_iterator(repo, args):
    start = args.start if not args.start is None else first_commit(repo)
    end = args.end

    start_commit, end_commit = validate_commit_range(repo, start, end)
    commits = list(repo.iter_commits(rev="{}..{}".format(start, end)))
    commits.append(start_commit)
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

    for commit in commits:
        print("MGMAIN_M: Checking out " + commit.hexsha + " in ", args.project_path, " (" + os.path.abspath(args.project_path) + ")")

if __name__ == '__main__':
    run_as_main()