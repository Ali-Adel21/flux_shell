import os
import readline

history_file = os.path.expanduser("~/.command_feedback")

try:
    readline.read_history_file(history_file)
except FileNotFoundError:
    pass

def save_history():
        try:
            history_length = readline.get_current_history_length()
        except FileNotFoundError:
            readline.write_history_file(history_file)