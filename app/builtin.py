import os 
import sys
from contextlib import redirect_stdout
import readline
from jobs import reap_jobs, BACKGROUND_JOBS


BUILTIN_CMDS = ["exit", "echo", "type", "pwd", "cd", "history", "complete", "jobs", "kill"]
CUSTOM_COMPLETERS = {}

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
        running_jobs = [j for j in BACKGROUND_JOBS if j["status"] == "Running"]
        if running_jobs:
            print("shell: you have running background jobs.")
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

    #Handle history
    elif cmd == "history":
        history_length = readline.get_current_history_length()
        all_items = [(i, readline.get_history_item(i)) for i in range(1, history_length + 1)]

        if args:
            if args[0] == "head" and len(args) > 1 and args[1].isdigit(): #Get history head
                limit = int(args[1])
                all_items = all_items[:limit]
            elif args[0] == "tail" and len(args) > 1 and args[1].isdigit():#Get history tail
                limit = int(args[1])
                all_items = all_items[-limit:]

        for idx, item in all_items:
            print(f"{idx} {item}", file=output_file)

    #Handle complete
    elif cmd == "complete":
        if len(args) >= 3 and args[0] == "-C":
            script_path = args[1]
            target_cmd = args[2]
            CUSTOM_COMPLETERS[target_cmd] = script_path

        elif len(args) >= 2 and args[0] == "-p":
            target_cmd = args[1]
            if target_cmd in CUSTOM_COMPLETERS:
                script_path = CUSTOM_COMPLETERS[target_cmd]
                print(f"complete -C {script_path} {target_cmd}", file=output_file)
            else:
                print(f"complete: {target_cmd}: no completion specification", file=error_file)
        
        elif len(args) >= 2 and args[0] == "-r":
            target_cmd = args[1]
            if target_cmd in CUSTOM_COMPLETERS:
                del CUSTOM_COMPLETERS[target_cmd]

    #Handle jobs
    elif cmd == "jobs":
        reap_jobs()
        for job in BACKGROUND_JOBS:
            print(f"[{job['id']}] {job['status']} {job['cmd']}", file=output_file)
    #handle kill
    elif cmd == "kill":
        if not args:
            print("kill: usage: kill <job_id_or_pid>")
            return
            
        target = args[0]
        killed = False
        clean_target = target.lstrip('%')
        if clean_target.isdigit():
            target_id = int(clean_target)
            for job in BACKGROUND_JOBS:
                if job["id"] == target_id:
                    try:
                        os.kill(job["pid"], 15)  #send termination signal to the process
                        print(f"Terminated job [{job['id']}] (PID {job['pid']})")
                        killed = True
                    except ProcessLookupError:
                        print(f"kill: process {job['pid']} not found")
                    break
        
        #otherwise, treat it as a direct OS Process ID
        if not killed and target.isdigit():
            pid = int(target)
            try:
                os.kill(pid, 15)
                print(f"Terminated PID {pid}")
                killed = True
            except ProcessLookupError:
                print(f"kill: ({pid}) - No such process")
                
        if not killed:
            print(f"kill: {target}: no such job or process")