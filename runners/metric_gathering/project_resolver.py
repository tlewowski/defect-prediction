from iresearch_context import IResearchContext
from project import Project
from projects.maven_project import MavenProject


def resolve_project(path: str, context: IResearchContext) -> Project:
    return MavenProject(path, context)