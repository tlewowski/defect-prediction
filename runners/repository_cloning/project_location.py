import subprocess

from metric_gathering.exec_resolver import resolve_full_path


class ProjectLocation:
    remote: str
    local: str
    target_rev: str | None

    def __init__(self, remote: str, local: str, target_rev: str | None):
        self.remote = remote
        self.local = local
        self.target_rev = target_rev
        self.git_path = resolve_full_path("git")

    def prepare(self):
        print("GITL: Preparing", self.remote, "to", self.local, " default:", self.target_rev)

        self.clone()
        if self.target_rev:
            self.checkout()

    def clone(self):
        args = [
            self.git_path,
            "clone"
        ]

        args.extend(["--", self.remote, self.local])
        print("GITL: Cloning with", args)
        subprocess.run(args)

    def checkout(self):
        args = [
            self.git_path,
            "checkout",
            self.target_rev
        ]

        print("GITL: Checking out with", args)
        subprocess.run(args, cwd=self.local)
