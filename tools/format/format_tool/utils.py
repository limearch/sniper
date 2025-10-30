# File: tools/format/format_tool/utils.py (REFACTORED - Complete Code)
# Description: This module contains utility functions for the 'format' tool.
# Its primary responsibility is to display the help screen by leveraging the
# centralized SNIPER help rendering engine.

import sys
import json
from pathlib import Path

# --- START: Core SNIPER Environment Integration ---
# This block is essential for the script to find and import modules from the 'lib' directory.
try:
    # We determine the project's root directory by traversing up from this file's location:
    # Path: .../sniper/tools/format/format_tool/utils.py
    # parents[3] will correctly resolve to the 'sniper/' directory.
    # Import the centralized environment instance and the help rendering function.
    from lib.sniper_env import env
    from lib.help_renderer import render_help

    # Set the logger name for this specific tool to provide context in log messages.
    env.log.name = "format"
except (ImportError, IndexError):
    # This is a critical failure. If the environment can't be loaded, the tool cannot run.
    print("\033[91m[CRITICAL ERROR]\033[0m Could not initialize the SNIPER environment.", file=sys.stderr)
    sys.exit(1)
# --- END: Core SNIPER Environment Integration ---

# --- START: Rich Library Integration ---
# We still need to ensure Rich is available, as it's a core dependency for the renderer.
try:
    from rich.console import Console
except ImportError:
    # If Rich is not installed, log a critical error using the env logger and exit.
    env.log.critical("The 'rich' library is required. Please run: pip install rich.")
    sys.exit(1)
# --- END: Rich Library Integration ---


def show_rich_help():
    """
    Displays the help screen for the 'format' tool.
    
    This function loads its UI description from the centralized JSON file
    (share/readme/format.json) and passes it to the central help renderer.
    This approach separates the help content from the presentation logic.
    """
    # Define the standardized path to this tool's help content file.
    help_file_path = env.ROOT_DIR / "share" / "readme" / "format.json"
    
    if not help_file_path.is_file():
        env.log.error(f"Help content file not found at: {help_file_path}")
        sys.exit(1)
        
    try:
        # Load the JSON data that describes the help screen's layout and content.
        with open(help_file_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
            
        # Call the central renderer with the loaded data object.
        # The renderer will handle all the complex Rich formatting.
        render_help(help_data)
        
    except (json.JSONDecodeError, IOError) as e:
        # Log any errors that occur during file reading or JSON parsing.
        env.log.error(f"Failed to load or parse help file '{help_file_path}': {e}")
        sys.exit(1)
        
    # Exit successfully after displaying the help message.
    sys.exit(0)

# The `check_command_exists` function has been removed from this file.
# The `generic_formatter.p
