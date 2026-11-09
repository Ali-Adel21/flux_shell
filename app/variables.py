import os
import re

# Local shell variables dictionary
shell_vars = {}

def is_valid_var_name(name: str) -> bool:
    return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name))

def set_variable(name: str, value: str):
    if not is_valid_var_name(name):
        raise ValueError(f"not a valid identifier: {name}")
    shell_vars[name] = value

def get_variable(name: str) -> str:
    if name in shell_vars:
        return shell_vars[name]
    return os.environ.get(name, "")

def expand_parameters(text: str) -> str:
    pattern = re.compile(r'\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}|\$([a-zA-Z_][a-zA-Z0-9_]*)')
    def replace_match(match):
        var_name = match.group(1) or match.group(2)
        return get_variable(var_name)   
    return pattern.sub(replace_match, text)