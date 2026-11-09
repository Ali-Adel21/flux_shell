import shutil
import subprocess
import os
import re
from .jobs import BACKGROUND_JOBS, get_next_job_id
from .variables import get_variable, set_variable, is_valid_var_name, expand_parameters
from .pipe import pipeline

def handle_external(cmd, args, stdout_file=None, stdout_mode="w", stderr_file=None, stderr_mode="w"):
    background = False

    if args and args[-1] == "&":
        background = True
        args.pop()
        
    if os.path.sep in cmd or os.path.altsep and os.path.altsep in cmd:
        executable_path = cmd if os.path.isfile(cmd) and os.access(cmd, os.X_OK) else None
    else:
        executable_path = shutil.which(cmd)
        
    if executable_path:
        stdout_target = None
        stderr_target = None
        try:
            if stdout_file:
                stdout_target = open(stdout_file, stdout_mode)
            if stderr_file:
                stderr_target = open(stderr_file, stderr_mode)

            if background:
                process = subprocess.Popen( 
                    [executable_path] + args,
                    stdout = stdout_target,
                    stderr = stderr_target,
                    preexec_fn=os.setsid
                )
                job_id = get_next_job_id()

                job_info = {
                    "id": job_id,
                    "pid": process.pid,
                    "process": process,
                    "cmd": " ".join([cmd] + args),
                    "status": "Running"
                }
                BACKGROUND_JOBS.append(job_info)
                print(f"[{job_id}] {process.pid}")

                stdout_target = None
                stderr_target = None
            else:

                subprocess.run([executable_path] + args, stdout=stdout_target, stderr=stderr_target)
            
        except Exception as e:
            print(f"{cmd}: {e}")
        finally:
            if stdout_target:
                stdout_target.close()
            if stderr_target:
                stderr_target.close()
    else:
        print(f"{cmd}: command not found")



def handle_assignment_if_present(command_string: str) -> bool:
    stripped = command_string.strip()
    if "=" in stripped and not stripped.startswith("declare") and not stripped.startswith("export"):
        parts = stripped.split("=", 1)
        if len(parts) == 2:
            name = parts[0].strip()
            value = parts[1].strip()
            if is_valid_var_name(name):
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                set_variable(name, expand_parameters(value))
                return True
    return False

