import os
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
        self.name = self._name_from_pom()
        self.context = context

    def build(self):
        tool = self.context.build_tool('maven')
        build_wd = self.context.build_wd(self)
        print("MVNP: building classes for:", self.name, "in", build_wd)

        tool.build(self, build_wd)

    def _name_from_pom(self) -> str:
        pom_path = os.path.join(self.src_path, 'pom.xml')
        tree = ET.parse(pom_path)

        artifact_id = tree.findtext("./mvn:artifactId", namespaces=MVN_NS)
        if artifact_id is None:
            print("MVNP: failed to find artifactId in", pom_path, "falling back to basename")
            return os.path.basename(self.src_path)
        else:
            return artifact_id
