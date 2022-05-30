import subprocess

from metric_gathering.exec_resolver import resolve_full_path


def get_project_history(src: str) -> list[str]:
    args = [
        resolve_full_path('git'),
        "log",
        "--format=format:%H",
        "--all"
    ]

    return subprocess.run(args, cwd=src, capture_output=True).stdout.decode('utf-8').splitlines(keepends=False)
