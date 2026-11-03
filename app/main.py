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
        
        redirect_stdout_file = None
        redirect_stdout_mode = "w"
        redirect_stderr_file = None
        redirect_stderr_mode = "w"
        new_parts = []
        i =0

        while i < len(parts):
            part = parts[i]
            #Handle stdout redirection
            if part in [">", "1>"]:
                if i + 1 < len(parts):
                    redirect_stdout_file = parts[i + 1]
                    redirect_stdout_mode = "w" #write
                    i += 2
                    continue
            elif part in [">>", "1>>"]:
                if i + 1 < len(parts):
                    redirect_stdout_file = parts[i + 1]
                    redirect_stdout_mode = "a" #append
                    i += 2
                    continue
            #Handle stderr redirection
            elif part == "2>":
                if i + 1 < len(parts):
                    redirect_stderr_file = parts[i + 1]
                    redirect_stderr_mode = "w" #write
                    i += 2
                    continue
            elif part == "2>>":
                if i + 1 < len(parts):
                    redirect_stderr_file = parts[i + 1]
                    redirect_stderr_mode = "a" #append
                    i += 2
                    continue
            
            new_parts.append(part)
            i += 1

        parts = new_parts
        if not parts:
            continue

        cmd = parts[0]
        args = parts[1:]

        if cmd in BUILTIN_CMDS:
            handle_builtin(cmd, args, redirect_stdout_file, redirect_stdout_mode, redirect_stderr_file, redirect_stderr_mode)
        else:
            handle_external(cmd, args, redirect_stdout_file, redirect_stdout_mode, redirect_stderr_file, redirect_stderr_mode)
if __name__ == "__main__":
    main()