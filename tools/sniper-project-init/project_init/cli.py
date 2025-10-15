# File: project_init/cli.py (REFACTORED - Complete Code)
# Description: The main command-line interface for the sniper-init tool.
# This file handles argument parsing, orchestrates the interactive and direct modes,
# and calls the core project creation logic.

import os
import sys
import json
import argparse
import questionary
from datetime import datetime
import jinja2
from pathlib import Path
# --- START: Core SNIPER Environment Integration ---
# This block ensures that the script can find and import the centralized 'env' object
# and the central help renderer.
try:
    # We determine the project's root directory by traversing up from this file's location.
    # __file__ -> .../sniper/tools/sniper-project-init/project_init/cli.py
    # parents[3] -> .../sniper/
    
    # Import the centralized environment instance and the help rendering function.
    from lib.sniper_env import env
    from lib.help_renderer import render_help

    # Set the logger name for this specific tool to provide context in log messages.
    env.log.name = "sniper-init"
except (ImportError, IndexError):
    # This is a critical failure. If the environment can't be loaded, the tool cannot run.
    print("\033[91m[CRITICAL ERROR]\033[0m Could not initialize the SNIPER environment.", file=sys.stderr)
    print("  ↳ Please ensure this tool is run from within the complete SNIPER project structure.", file=sys.stderr)
    sys.exit(1)
# --- END: Core SNIPER Environment Integration ---

# --- START: Rich Library Integration ---
# Import Rich library components for a modern UI.
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.align import Align
except ImportError:
    # If Rich is not installed, log a critical error and exit.
    env.log.critical("The 'rich' library is required for the UI. Please run: pip install rich.")
    sys.exit(1)
# --- END: Rich Library Integration ---

# Import the core logic after the environment has been successfully set up.
from .core import create_project

# Initialize a Rich console for printing UI elements.
console = Console()


def get_available_templates(templates_dirs: list) -> list:
    """
    Scans a list of template directories and returns a unique, sorted list of available templates.
    
    Args:
        templates_dirs (list): A list of Path objects to scan for template folders.
    
    Returns:
        A sorted list of template names (directory names).
    """
    templates = set()
    for dir_path in templates_dirs:
        if dir_path and dir_path.is_dir():
            # Scan the directory and add any subdirectories that do not start with '.'
            templates.update([d.name for d in dir_path.iterdir() if d.is_dir() and not d.name.startswith('.')])
    return sorted(list(templates))


def load_template_manifest(template_name: str, templates_dirs: list) -> dict:
    """
    Loads the 'sniper.json' manifest file for a given template name.
    It searches for the manifest in the provided list of template directories.
    
    Args:
        template_name (str): The name of the template to load.
        templates_dirs (list): The directories to search within.
        
    Returns:
        A dictionary with the manifest data, or an empty dict if not found or invalid.
    """
    for dir_path in templates_dirs:
        if not dir_path: continue
        manifest_path = dir_path / template_name / 'sniper.json'
        if manifest_path.is_file():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Log an error if the JSON is malformed.
                env.log.error(f"Invalid JSON in manifest file: {manifest_path}")
    return {}


def show_rich_help(available_templates: list):
    """
    Displays the help screen by loading its UI description from a JSON file
    and passing it to the central help renderer.
    """
    help_file_path = env.ROOT_DIR / "share" / "readme" / "sniper-init.json"
    
    if not help_file_path.is_file():
        env.log.error(f"Help file not found at: {help_file_path}")
        sys.exit(1)
        
    try:
        with open(help_file_path, 'r', encoding='utf-8') as f:
            help_data = json.load(f)
            
        # --- Dynamic Data Injection ---
        # We dynamically insert the list of available templates into the loaded help data.
        # This combines the static structure of JSON with dynamic runtime information.
        for panel in help_data.get("layout", []):
            if panel.get("title") == "[blue]Usage & Options[/]":
                for content_item in panel.get("content", []):
                    if content_item.get("component") == "Markup":
                        # Find the placeholder line and replace it.
                        updated_text = []
                        for line in content_item.get("text", []):
                            if "[dim]Available:" in line:
                                line = f"                     [dim]Available: {', '.join(available_templates) or 'None'}[/]"
                            updated_text.append(line)
                        content_item["text"] = updated_text
                        break
                break

        # Call the central renderer with the final, complete data object.
        render_help(help_data)
        
    except (json.JSONDecodeError, IOError) as e:
        env.log.error(f"Failed to load or parse help file '{help_file_path}': {e}")
        sys.exit(1)
        
    sys.exit(0)


def print_rich_summary(name: str, template: str, manifest: dict, variables: dict):
    """
    Displays a beautiful, partitioned summary panel after a project is created successfully.
    """
    console.print()
    summary_table = Table(box=None, show_header=False, expand=True)
    summary_table.add_column("Property", style="bold magenta", justify="right", width=15)
    summary_table.add_column("Value", style="cyan")
    summary_table.add_row("Project Name", name)
    summary_table.add_row("Template", template)
    summary_table.add_row("Location", os.path.abspath(name))
    summary_table.add_row("Created On", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    next_steps_text = Text("\n")
    # Get 'next_steps' from the manifest, with a sensible default.
    steps = manifest.get('next_steps', [f"cd {name}"])
    for i, step in enumerate(steps, 1):
        # Render Jinja2 variables within the next steps for dynamic instructions.
        rendered_step = jinja2.Template(step).render(variables)
        next_steps_text.append(f"  {i}. {rendered_step}\n", style="default")
    
    console.print(Panel(summary_table, title="[bold green]✅ Project Created Successfully[/]", border_style="green"))
    console.print(Panel(Align.left(next_steps_text), title="[bold yellow]Next Steps[/]", border_style="yellow"))
    console.print(Align.center(Text("Happy Coding!", style="bold magenta")))


def main():
    """
    Main entry point for the sniper-init command.
    """
    # --- Template Path Configuration ---
    # The default templates are bundled with the tool.
    tool_dir = Path(__file__).parent.parent
    default_templates_dir = tool_dir / 'templates'
    
    # Check the central SNIPER config for a custom templates directory.
    project_init_config = env.config.get('sniper-project-init', {})
    custom_templates_path = project_init_config.get('custom_templates_dir')
    custom_templates_dir = Path(custom_templates_path) if custom_templates_path else None
    
    templates_dirs = [default_templates_dir, custom_templates_dir]
    available_templates = get_available_templates(templates_dirs)

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("name", nargs='?')
    parser.add_argument("-t", "--template", choices=available_templates)
    parser.add_argument("--no-git", action="store_false", dest="git", default=True)
    parser.add_argument("--with-docker", action="store_true", dest="docker", default=None)
    parser.add_argument("--no-docker", action="store_false", dest="docker", default=None)
    parser.add_argument('-h', '--help', action='store_true')
    args = parser.parse_args()
    
    if args.help or (len(sys.argv) == 1 and not sys.stdin.isatty()):
        show_rich_help(available_templates)

    # --- Prepare Variables for Jinja2 Templating ---
    # Fetch default user info from the centralized SNIPER config file.
    user_config = env.config.get('user', {})
    variables = {
        "author_name": user_config.get('author_name', 'Your Name'),
        "author_email": user_config.get('author_email', 'your@email.com'),
        "year": datetime.now().year
    }
    options = {}
    name = ""
    template = ""
    manifest = {}

    try:
        if not args.name:
            # --- Interactive Mode ---
            console.print(Panel(Text("SNIPER: Interactive Project Setup", style="bold magenta", justify="center")))
            name = questionary.text("Project name:").ask()
            if not name: return

            template = questionary.select("Select project type:", choices=available_templates).ask()
            if not template: return

            manifest = load_template_manifest(template, templates_dirs)
            for question in manifest.get('questions', []):
                answer = questionary.text(question['prompt'], default=str(question.get('default', ''))).ask()
                variables[question['key']] = answer

            git = questionary.confirm("Initialize a Git repository?", default=True).ask()
            docker = questionary.confirm("Include Docker files?", default=True).ask()
            license_choice = questionary.select("Choose a license:", choices=['None', 'MIT', 'Apache 2.0'], default='MIT').ask()
            options = {'git': git, 'docker': docker, 'license': license_choice if license_choice != 'None' else None}
        else:
            # --- Direct Mode ---
            if not args.template:
                env.log.error("A template must be specified with '-t' in direct mode.")
                sys.exit(1)
            name = args.name
            template = args.template
            manifest = load_template_manifest(template, templates_dirs)
            # Use default values for any template-specific questions in direct mode.
            for question in manifest.get('questions', []):
                variables[question['key']] = question.get('default', '')
            
            # If neither --with-docker nor --no-docker is specified, default to True.
            docker_option = True if args.docker is None else args.docker
            options = {'git': args.git, 'docker': docker_option, 'license': 'MIT'} # Use a sensible default license
            
    except (KeyboardInterrupt, TypeError):
        # Handle Ctrl+C gracefully during user prompts.
        env.log.warning("Operation cancelled by user.")
        return

    # Add project-specific variables for Jinja2 rendering.
    variables.update({"project_name": name, "project_type": template})
    
    # Determine which template directory contains the chosen template.
    template_dir_to_use = custom_templates_dir if custom_templates_dir and (custom_templates_dir / template).is_dir() else default_templates_dir
    
    # Pass the console object to the core function for displaying status updates.
    success, error = create_project(name, template, template_dir_to_use, variables, options, manifest, console)

    if success:
        print_rich_summary(name, template, manifest, variables)
    else:
        env.log.error(f"Project creation failed: {error}")
        sys.exit(1)
