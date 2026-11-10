import os 
import sys
import shlex
import shutil
from .variables import expand_parameters
import signal

def pipeline(command_string):
    op_split = command_string.split("|")
    pipeline_cmds = [shlex.split(segment.strip()) for segment in op_split]

    num_cmds = len(pipeline_cmds)

    if num_cmds == 1:
        return 

    pipes = [os.pipe() for _ in range(num_cmds - 1)]

    pids= []
    for i, cmd_args in enumerate(pipeline_cmds):
        expanded_args = [expand_parameters(arg) for arg in cmd_args]

        clean_args = []
        redirect_file = None
        redirect_mode = "w"

        j = 0
        while j < len(expanded_args):
            arg = expanded_args[j]
            if arg in [">", "1>"]:
                if j + 1 < len(expanded_args):
                    redirect_file = expand_parameters(expanded_args[j + 1])
                    redirect_mode = "w"
                    j += 2
                    continue
            elif arg in [">>", "1>>"]:
                if j + 1 < len(expanded_args):
                    redirect_file = expand_parameters(expanded_args[j + 1])
                    redirect_mode = "a"
                    j += 2
                    continue
            clean_args.append(arg)
            j += 1
            
        cmd_args = clean_args

        pid = os.fork()

        if pid == 0:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            if i > 0:
                read_fd, _ = pipes[i - 1]
                os.dup2(read_fd, 0)

            if i < num_cmds - 1:
                _, write_fd = pipes[i]
                os.dup2(write_fd, 1)
            elif redirect_file:
                flags = os.O_WRONLY | os.O_CREAT | (os.O_APPEND if redirect_mode == "a" else os.O_TRUNC)
                fd = os.open(redirect_file, flags, 0o666)
                os.dup2(fd, 1)
                os.close(fd)

            for r, w in pipes:
                os.close(r)
                os.close(w)

            if not clean_args:
                sys.exit(0)

            executable = shutil.which(clean_args[0])

            if not executable:
                print(f"command not found: {cmd_args[0]}", file=sys.stderr)
                sys.exit(127)

            try:
                os.execvp(executable, cmd_args)
            except Exception as e:
                print(f"flux: {e}", file=sys.stderr)
                sys.exit(1)

        else:
            pids.append(pid)

    for r, w in pipes:
        os.close(r)
        os.close(w)

    for pid in pids:
        os.waitpid(pid, 0)