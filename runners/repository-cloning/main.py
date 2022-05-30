import argparse
import csv
import os
import re
import subprocess


class ProjectLocation:
    remote: str
    local: str
    target_rev: str | None

    def __init__(self, remote: str, local: str, target_rev: str | None):
        self.remote = remote
        self.local = local
        self.target_rev = target_rev

    def prepare(self):
        print("GITL: Preparing", self.remote, "to", self.local, " default:", self.target_rev)

        self.clone()
        if self.target_rev:
            self.checkout()

    def clone(self):
        args = [
            "git",
            "clone"
        ]

        args.extend(["--", self.remote, self.local])
        print("GITL: Cloning with", args)
        subprocess.run(args)

    def checkout(self):
        args = [
            "git",
            "checkout",
            self.target_rev
        ]

        print("GITL: Checking out with", args)
        subprocess.run(args, cwd=self.local)


def run_as_main():
    parser = argparse.ArgumentParser(description="Calculate software project product metrics")
    parser.add_argument("--projects_path", type=str, help="directory where projects will be cloned to", required=True)
    parser.add_argument("--list", type=str, help="path to a CSV file with list of projects to clone", required=True)

    args = parser.parse_args()
    projects = []
    with open(args.list) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            url = row[0]
            project_name = re.search(".*/([^/]+).git/?", url)
            if(project_name[1] is None):
                print("RCMAIN: Failed to find name for project:", url, ". Skipping it.")
                continue

            projects.append(ProjectLocation(url, os.path.join(args.projects_path, project_name[1]), row[1]))

    print("RCMAIN: Will attempt to download", len(projects), "projects")

    for p in projects:
        p.prepare()

    print("RCMAIN: Finished")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_as_main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
