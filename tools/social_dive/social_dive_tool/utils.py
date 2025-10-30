# File: tools/social_dive/social_dive_tool/utils.py (REFACTORED - Complete Code)
# Description: This module contains utility functions for the social-dive tool,
# including the help display and category listing logic.

import json
from pathlib import Path
import sys

# --- START: Core SNIPER Environment Integration ---
try:
    # This path is relative to this file's location: .../tools/social_dive/social_dive_tool/utils.py
    _PROJECT_ROOT = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(_PROJECT_ROOT))
    
    from lib.sniper_env import env
    from lib.help_renderer import render_help

    # Set the logger name for this specific tool.
    env.log.name = "social-dive"
except (ImportError, IndexError):
    print("\033[91m[CRITICAL ERROR]\033[0m Could not initialize the SNIPER environment.", file=sys.stderr)
    sys.exit(1)
# --- END: Core SNIPER Environment Integration ---


def show_rich_help():
    """
    Displays the help screen by loading its UI description from the centralized
    JSON file and passing it to the central help renderer.
    """
    help_file_path = env.ROOT_DIR / "share" / "readme" / "social-dive.json"
    
    if not help_file_path.is_file():
        env.log.error(f"Help file not found at: {help_file_path}")
        sys.exit(1)
        
    try:
        # Load the JSON data that describes the help screen's layout and content.
        with open(help_file_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
            
        # Call the central renderer with the loaded data object.
        render_help(help_data)
        
    except (json.JSONDecodeError, IOError) as e:
        # Log any errors that occur during file reading or JSON parsing.
        env.log.error(f"Failed to load or parse help file '{help_file_path}': {e}")
        sys.exit(1)
        
    # Exit successfully after displaying the help message.
    sys.exit(0)


def get_categories():
    """
    Reads the 'data.json' file to find and return all unique site categories.
    
    Returns:
        A sorted list of category names (strings).
    """
    try:
        # Construct the path to data.json relative to this file's location.
        data_file_path = Path(__file__).parent / "data.json"
        with open(data_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Use a set to automatically handle uniqueness, then convert to a sorted list.
        categories = set(info.get("category", "Uncategorized").capitalize() for info in data.values())
        return sorted(list(categories))
    except FileNotFoundError:
        env.log.error("The site data file 'data.json' was not found in the tool's directory.")
        return []
    except json.JSONDecodeError:
        env.log.error("Failed to parse 'data.json'. The file may be corrupted.")
        return []
