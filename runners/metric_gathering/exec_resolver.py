import os
import subprocess

cached = {}
def resolve_full_path(binary: str, required: bool = True) -> str | None:
    if binary in cached:
        v = cached[binary]
        print("EXECR: returning {} from cache: {}".format(binary, v))
        return v

    found = None
    if os.name == 'nt':
        found = subprocess.run(['where', binary], shell=True, capture_output=True).stdout.decode('utf-8').splitlines(False)
        found = [c for c in found if c.endswith(".cmd") or c.endswith(".exe")]
    else:
        found = subprocess.run(['which', binary], capture_output=True).stdout.decode('utf-8').splitlines(False)

    if found is None or not found:
        print("EXECR: failed to find", binary)
        if required:
            raise RuntimeError("Required {}, but not found it".format(binary))
    else:
        found = found[0]
        cached[binary] = found
        print("EXECR: found", binary, "in", found)

    return found
