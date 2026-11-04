import shutil
import subprocess
import os
#tracking for background jobs
BACKGROUND_JOBS = []

def reap_jobs():
    global BACKGROUND_JOBS
    remaining_jobs = []
    
    for job in BACKGROUND_JOBS:
        if job["status"] == "Running":
            try:
                pid, status = os.waitpid(job["pid"], os.WNOHANG)
                if pid != 0:
                    job["status"] = "Done"

                    if os.WIFEXITED(status):
                        exit_code = os.WEXITSTATUS(status)
                        job["exit_code"] = exit_code
                    else:
                        job["exit_code"] = None
                        print(f"[{job['id']}]+ Done (exit: {job.get('exit_code', 0)}) {job['cmd']}")
            except ChildProcessError:
                job["status"] = "Done"
                print(f"[{job['id']}]+ Done {job['cmd']}")
               

        if job["status"] == "Running":
            remaining_jobs.append(job)
            
    BACKGROUND_JOBS.clear()
    BACKGROUND_JOBS.extend(remaining_jobs)

def get_next_job_id():
    if not BACKGROUND_JOBS:
        return 1
    return max(job["id"] for job in BACKGROUND_JOBS) + 1


def handle_external(cmd, args, stdout_file=None, stdout_mode="w", stderr_file=None, stderr_mode="w"):
    global BACKGROUND_JOBS
    background = False

    if args and args[-1] == "&":
        background = True
        args.pop()
        
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
                    stderr = stderr_target
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