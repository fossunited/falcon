from pathlib import Path

def get_module_relative_path(path):
    root = Path(__file__).parent / path
    return str(root)

templates_dir = get_module_relative_path("templates")
static_dir = get_module_relative_path("static")
