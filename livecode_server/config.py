"""Configuration for livecode.

The config file can be specified using envionment variable
FALCON_CONFIG_FILE.

A sample config file config_sample.yml is provided in the repo.
"""
import os
import yaml

DEFAULT_CONFIG = {
    "runtimes": {
        "python": {
            "image": "fossunited/falcon-python:3.9",
            "command": [],
            "code_filename": "main.py"
        },
        "javascript": {
            "image": "frappe/falcon-javascript:latest",
            "command": [],
            "code_filename": "main.js"
        }
        "rust": {
            "image": "fossunited/falcon-rust",
            "command": [],
            "code_filename": "main.rs"
        },
        "golang": {
            "image": "fossunited/falcon-golang",
            "command": [],
            "code_filename": "main.go"
        },
        "joy": {
            "image": "falcon-joy",
            "command": ["python", "/opt/start.py"],
            "code_filename": "main.py"
        },
        "python-canvas": {
            "image": "livecode-python-canvas",
            "command": ["python", "/opt/startup.py"],
            "code_filename": "main.py"
        }
    }
}

def read_config():
    config_file = os.getenv("FALCON_CONFIG_FILE")
    if config_file:
        return yaml.safe_load(open(config_file))
    else:
        return {}

CONFIG = read_config()

def _get_runtime(config, name):
    return config.get('runtimes', {}).get(name)

def get_runtime(name):
    return _get_runtime(CONFIG, name) or _get_runtime(DEFAULT_CONFIG, name)

def has_runtime(name):
    return get_runtime(name) is not None
