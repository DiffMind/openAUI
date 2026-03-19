import subprocess
from typing import List
import shlex
import re, os

child_env = os.environ.copy()

# 2. ?? locale ??????????????
child_env.update(
    {
        "LC_ALL": "en_US.UTF-8",
        "LANG": "en_US.UTF-8",
        "LANGUAGE": "en_US",
        "LC_MESSAGES": "en_US.UTF-8",
    }
)

proc = subprocess.Popen(
    ["bash"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    env=child_env,
)


def run_cmd_list(cmd: List[str]):
    cmd_str = " ".join(shlex.quote(x) for x in cmd)
    response, _ = run_cmd(cmd_str)
    return response


# def run_cmd(cmd_str: str):
#     cmd_str += "; echo __END__\n"
#     proc.stdin.write(cmd_str)
#     proc.stdin.flush()
#     output = []
#     while True:
#         line = proc.stdout.readline()
#         if not line:
#             break

#         if "__END__" in line:
#             break

#         output.append(line)


#     return "".join(output)
def run_cmd(cmd_str: str):
    cmd_str += "; echo $?; echo __END__\n"
    proc.stdin.write(cmd_str)
    proc.stdin.flush()

    output = []
    exit_code = None

    while True:
        line = proc.stdout.readline()
        if not line:
            break

        if line.strip().isdigit() and exit_code is None:
            exit_code = int(line.strip())
            continue

        if "__END__" in line:
            break

        output.append(line)

    return "".join(output), exit_code


COMMON_COMMANDS = {
    "sudo",
    "ls",
    "cd",
    "pwd",
    "cat",
    "echo",
    "touch",
    "mkdir",
    "rm",
    "cp",
    "mv",
    "grep",
    "find",
    "chmod",
    "chown",
    "ps",
    "kill",
    "top",
    "df",
    "du",
    "head",
    "tail",
    "python",
    "pip",
    "git",
    "vim",
    "nano",
    "clear",
    "apt",
}

SHELL_OPERATORS = ["|", "&&", "||", ">", ">>", "<", "*"]


def is_shell_command(text: str) -> bool:
    text = text.strip()
    if not text:
        return False

    # ? Clearly natural language
    if re.search(r"[???]", text):
        return False

    # ? Words indicating natural language
    if re.search(r"\b(what|how|why|can|should)\b", text.lower()):
        return False

    # ? Shell operators (strong indicator)
    if any(op in text for op in SHELL_OPERATORS):
        return True

    parts = text.split()

    # ? First word matches common commands
    if parts[0] in COMMON_COMMANDS:
        return True

    # ? Path-like patterns
    if re.search(r"^(\.|/|~)", parts[0]):
        return True

    # ? Has parameters (like -l, --help)
    if len(parts) > 1 and parts[1].startswith("-"):
        return True

    return False
