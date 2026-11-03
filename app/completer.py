import os
import glob
import readline
from builtin import BUILTIN_CMDS

def shell_completer(text, state):
    line_buffer = readline.get_line_buffer()

    if " " not in line_buffer.lstrip():
        matches = [cmd for cmd in BUILTIN_CMDS if cmd.startswith(text)]
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