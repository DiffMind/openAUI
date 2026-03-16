import subprocess
from typing import List


def run_cmd(cmd: List[str]) -> str:
    cmd_to_run = cmd.copy()
    proc = subprocess.run(
        cmd_to_run,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=300,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        return proc.stderr
    return proc.stdout
