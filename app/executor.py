import shutil
import subprocess
import os
from jobs import BACKGROUND_JOBS, get_next_job_id

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