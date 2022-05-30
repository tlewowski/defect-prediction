from project import Project


class MetricsTool:
    name: str

    def analyze(self, project: Project) -> str:
        pass

    def normalize_results(self, raw_results_path: str, project: Project) -> str:
        pass
