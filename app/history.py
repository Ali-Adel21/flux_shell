import os
import readline

history_file = os.path.expanduser("~/.shell_history")

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            readline.read_history_file(HISTORY_FILE)
        except Exception as e:
            pass

def save_history():
    try:
        readline.set_history_length(100)
        readline.write_history_file(HISTORY_FILE)
    except Exception as e:
        pass