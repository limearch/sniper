# Handles loading and creating user configuration
# project_init/config.py
import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "sniper-init"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "author_name": "",
    "author_email": "",
    "custom_templates_dir": ""
}

def ensure_config_exists():
    """Creates the config file with defaults if it doesn't exist."""
    if not CONFIG_FILE.is_file():
        print(f"\033[94m[INFO]\033[0m Creating default config at: {CONFIG_FILE}")
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)

def load_config():
    """Loads the user's configuration."""
    ensure_config_exists()
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)