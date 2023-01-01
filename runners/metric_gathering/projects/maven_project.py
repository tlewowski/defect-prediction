import os
import subprocess
import xml.etree.ElementTree as ET

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
        self.name = self._name_from_pom()
        self.context = context
        self.revision = self._revision_from_src()

    def build(self):
        tool = self.context.build_tool('maven')
        local_repo = self.context.global_cache_dir(self)
        print("MVNP: building classes for:", self.name, "with libraries from", local_repo)

        tool.build(self, local_repo)

    def _name_from_pom(self) -> str:
        pom_path = os.path.join(self.src_path, 'pom.xml')
        tree = ET.parse(pom_path)

        artifact_id = tree.findtext("./mvn:artifactId", namespaces=MVN_NS)
        if artifact_id is None:
            print("MVNP: failed to find artifactId in", pom_path, "falling back to basename")
            return os.path.basename(self.src_path)
        else:
            return artifact_id

    def _revision_from_src(self) -> str:
        git_path = self.context.binary_path('git')
        args = [git_path, 'rev-parse', 'HEAD']
        rev = subprocess.run(args, capture_output=True, cwd=self.src_path).stdout.decode("utf-8").strip()
        if not rev:
            print("MVNP: failed to resolve version. Using 'unknown'")
            return 'unknown'
        else:
            return rev
