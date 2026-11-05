import signal

def setup_signals():#Make the shell ignore ctrl C when a child process running
   signal.signal(signal.SIGINT, signal.default_int_handler)