import os

from git import Repo
from iresearch_context import IResearchContext
from project import Project

MVN_NS = {
    'mvn': 'http://maven.apache.org/POM/4.0.0',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}


class MavenProject(Project):
    def __init__(self, src_path: str, context: IResearchContext):
        self.src_path = src_path
        self.build_path = src_path + '/target'
        self.name = os.path.basename(src_path)
        self.context = context
        self.revision = self._revision_from_src()

    def build(self):
        tool = self.context.build_tool('maven')
        local_repo = self.context.global_cache_dir(tool.name)
        print("MVNP: building classes for:", self.name, "with libraries from", local_repo)

        tool.build(self, local_repo)

    def _revision_from_src(self) -> str:
        return Repo(self.src_path).head.commit.hexsha
