import os
import glob
import shlex
import subprocess
import readline
from builtin import BUILTIN_CMDS, CUSTOM_COMPLETERS

_PATH_EXECUTABLES_CACHE = None

def get_path_executables(text):
    global _PATH_EXECUTABLES_CACHE
    if not text:
        return []

    if _PATH_EXECUTABLES_CACHE is None:
        executables = set()
        path_env = os.environ.get("PATH", "")
        for directory in path_env.split(os.pathsep):
            if os.path.isdir(directory):
                try:
                    for filename in os.listdir(directory):
                        full_path = os.path.join(directory, filename)
                        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                            executables.add(filename)
                except PermissionError:
                    continue
        _PATH_EXECUTABLES_CACHE = list(executables)
    return [ex for ex in _PATH_EXECUTABLES_CACHE if ex.startswith(text)]

def shell_completer(text, state):
    line_buffer = readline.get_line_buffer()

    try:
        parts = shlex.split(line_buffer)
    except ValueError:
        parts = line_buffer.split()

    if " " not in line_buffer.lstrip():
        builtin_matches = [cmd for cmd in BUILTIN_CMDS if cmd.startswith(text)]
        path_matches = get_path_executables(text)
        matches = sorted(list(set(builtin_matches + path_matches)))
    else:
        cmd = parts[0] if parts else ""
        if cmd in CUSTOM_COMPLETERS:
            script_path = CUSTOM_COMPLETERS[cmd]
            try:
                curr_word = text
                prev_word = parts[-2] if len(parts) > 1 else cmd
                result = subprocess.run(
                    [script_path, cmd, curr_word, prev_word],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                matches = result.stdout.splitlines()
            except Exception:
                matches = []
        else:
            path_pattern = text + "*"
            matches = glob.glob(path_pattern)
            matches = [
                m + "/" if os.path.isdir(m) else m 
                for m in matches
            ]

    if state < len(matches):
        return matches[state]
    else:
        return None

def setup_readline(history_file):
    try:
        readline.read_history_file(history_file)
    except FileNotFoundError:
        pass
    
    readline.set_completer(shell_completer)
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims(" \t\n`~!@#$%^&*()-=+[{]}\\|;:'\",<>?")