import os
import subprocess


def resolve_full_path(binary: str) -> str | None:
    found = None
    if os.name == 'nt':
        found = subprocess.run(['where', binary], shell=True, capture_output=True).stdout.decode('utf-8').splitlines(False)
        found = [c for c in found if c.endswith(".cmd") or c.endswith(".exe")]
    else:
        found = subprocess.run(['which', binary], shell=True, capture_output=True).stdout.decode('utf-8').splitlines(False)

    if found is None or not found:
        print("EXECR: failed to find", binary)
    else:
        found = found[0]
        print("EXECR: found", binary, "in", found)

    return found