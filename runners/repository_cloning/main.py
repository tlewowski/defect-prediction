import argparse
import csv
import os
import re

from repository_cloning.project_location import ProjectLocation


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
