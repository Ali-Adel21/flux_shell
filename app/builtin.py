import os 
import sys

BUILTIN_CMDS = ["exit", "echo", "type", "pwd", "cd"]

def handle_builtin(cmd, args):
    #Handle exit
    if cmd == "exit":
        sys.exit(int(args[0]) if args else 0)
    #Handle echo
    elif cmd == "echo":
        print(" ".join(args))
    #Handle type
    elif cmd == "type":
        if not args:
            print("type: missing argument")
        elif args[0] in BUILTIN_CMDS:
            print(f"{args[0]} is a shell builtin")
        else:
            path_env = os.environ.get("PATH", "")
            directories = path_env.split(os.pathsep) 
            found = False
            for directory in directories:
                candidate_path = os.path.join(directory, args[0])
                if os.path.isfile(candidate_path) and os.access(candidate_path, os.X_OK):
                    print(f"{args[0]} is {candidate_path}")
                    found = True
                    break
            if not found:
                print(f"{args[0]}: not found")
    #Handle pwd
    elif cmd == "pwd":
        print(os.getcwd())
    #handle cd
    elif cmd == "cd":
        if args:
            target_path = os.path.expanduser(args[0]) 
            try:
                os.chdir(target_path)
            except FileNotFoundError:
                print(f"cd: {args[0]}: No such file or directory")
            except NotADirectoryError:
                print(f"cd: {args[0]}: Not a directory")
            except PermissionError:
                print(f"cd: {args[0]}: Permission denied")