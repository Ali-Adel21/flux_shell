import os
import glob
import readline
from builtin import BUILTIN_CMDS


def get_path_executables(text):
    executables = set()
    path_env = os.environ.get("PATH", "")
    for directory in path_env.split(os.pathsep):
        if os.path.isdir(directories):
            try:
                for filename in os.listdir(directory):
                    if filename.startswith(text):
                        full_path = os.path.join(directory, filename)
                        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                            executables.add(filename)
            except PermissionError:
                continue
    return list(executables)

def shell_completer(text, state):
    line_buffer = readline.get_line_buffer()

    if " " not in line_buffer.lstrip():
        builtin_matches = [cmd for cmd in BUILTIN_CMDS if cmd.startswith(text)]
        path_matches = get_path_executables(text)
        matches = sorted(list(set(builtin_matches + path_matches)))
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