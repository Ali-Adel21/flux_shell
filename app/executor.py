import shutil
import subprocess

def handle_external(cmd, args):
    executable_path = shutil.which(cmd)
    if executable_path:
        try:
            subprocess.run([cmd] + args)
        except Exception as e:
            print(f"{cmd}: {e}")
    else:
        print(f"{cmd}: command not found")