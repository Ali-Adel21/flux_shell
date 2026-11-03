import shutil
import subprocess

def handle_external(cmd, args, stdout_file=None, stdout_mode="w", stderr_file=None, stderr_mode="w"):
    executable_path = shutil.which(cmd)
    if executable_path:
        stdout_target = None
        stderr_target = None
        try:
            if stdout_file:
                stdout_target = open(stdout_file, stdout_mode)
            if stderr_file:
                stderr_target = open(stderr_file, stderr_mode)
            
            subprocess.run([cmd] + args, stdout=stdout_target, stderr=stderr_target)
            
        except Exception as e:
            print(f"{cmd}: {e}")
        finally:
            if stdout_target:
                stdout_target.close()
            if stderr_target:
                stderr_target.close()
    else:
        print(f"{cmd}: command not found")