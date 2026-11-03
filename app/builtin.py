import os 
import sys
from contextlib import redirect_stdout


BUILTIN_CMDS = ["exit", "echo", "type", "pwd", "cd"]

def handle_builtin(cmd, args, stdout_file=None, stdout_mode="w", stderr_file=None, stderr_mode="w"):
    out_file = open(stdout_file, stdout_mode) if stdout_file else sys.stdout
    err_file = open(stderr_file, stderr_mode) if stderr_file else sys.stderr
    
    try:
        _execute_builtin(cmd, args, output_file=out_file, error_file=err_file)
    finally:
        if stdout_file and out_file != sys.stdout:
            out_file.close()
        if stderr_file and err_file != sys.stderr:
            err_file.close()

def _execute_builtin(cmd, args, output_file=sys.stdout, error_file=sys.stderr):
    #Handle exit
    if cmd == "exit":
        sys.exit(int(args[0]) if args else 0)
    #Handle echo
    elif cmd == "echo":
        print(" ".join(args), file=output_file)
    #Handle type
    elif cmd == "type":
        if not args:
            print("type: missing argument", file=error_file)
        elif args[0] in BUILTIN_CMDS:
            print(f"{args[0]} is a shell builtin", file=output_file)
        else:
            path_env = os.environ.get("PATH", "")
            directories = path_env.split(os.pathsep) 
            found = False
            for directory in directories:
                candidate_path = os.path.join(directory, args[0])
                if os.path.isfile(candidate_path) and os.access(candidate_path, os.X_OK):
                    print(f"{args[0]} is {candidate_path}", file=output_file)
                    found = True
                    break
            if not found:
                print(f"{args[0]}: not found", file=error_file)
    #Handle pwd
    elif cmd == "pwd":
        print(os.getcwd(), file=output_file)
    #handle cd
    elif cmd == "cd":
        if args:
            target_path = os.path.expanduser(args[0]) 
            try:
                os.chdir(target_path)
            except FileNotFoundError:
                print(f"cd: {args[0]}: No such file or directory", file=error_file)
            except NotADirectoryError:
                print(f"cd: {args[0]}: Not a directory", file=error_file)
            except PermissionError:
                print(f"cd: {args[0]}: Permission denied", file=error_file)