import os
import subprocess

from git import Repo
from iresearch_context import IResearchContext
from project import Project

class RawProject(Project):
    def __init__(self, src_path: str, context: IResearchContext):
        self.src_path = src_path
        self.build_path = src_path + '/target'
        self.name = os.path.basename(src_path)
        self.context = context
        self.revision = self._revision_from_src()

    def build(self):
        raise RuntimeError("RAWP: Cannot build a raw project", self.name, "at", self.src_path)

    def _revision_from_src(self) -> str:
        return Repo(self.src_path).head.commit.hexsha
