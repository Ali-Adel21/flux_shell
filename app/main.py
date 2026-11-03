import os
import sys
import getpass
import socket
import shlex
import atexit
import readline

from completer import setup_readline
from builtin import BUILTIN_CMDS, handle_builtin
from executor import handle_external

def main():
    username = getpass.getuser()
    hostname = socket.gethostname()

    GREEN = "\001\033[1;32m\002"
    BLUE = "\001\033[1;34m\002"
    WHITE = "\001\033[1;37m\002"
    RESET = "\001\033[0m\002"

    history_file = os.path.expanduser("~/.command_feedback")
    setup_readline(history_file)
    atexit.register(readline.write_history_file, history_file)

    while True:
        current_dir = os.path.basename(os.getcwd()) or "/"
        prompt = f"{GREEN}{username}@{hostname}{RESET}:{BLUE}{current_dir}{RESET}{WHITE} $ {RESET}"
        
        try:
            command = input(prompt)
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not command.strip():
            continue

        parts = shlex.split(command)
        if not parts:
            continue

        cmd = parts[0]
        args = parts[1:]

        if cmd in BUILTIN_CMDS:
            handle_builtin(cmd, args)
        else:
            handle_external(cmd, args)

if __name__ == "__main__":
    main()