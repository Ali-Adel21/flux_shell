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