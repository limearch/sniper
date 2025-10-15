# File: project_init/core.py (REFACTORED - Complete Code)
# Description: Contains the core logic for creating the project structure,
# processing templates, and running post-initialization commands.

import os
import shutil
import subprocess
import jinja2
import questionary

# --- START: Core SNIPER Environment Integration ---
# This module is imported by the main CLI, which has already set up the Python path.
# We can directly import the 'env' object.
try:
    from lib.sniper_env import env
except ImportError:
    # This fallback provides a dummy object if the module is run in isolation for testing.
    # It prevents the script from crashing and prints basic messages.
    print("\033[91m[CRITICAL ERROR]\033[0m Could not import SNIPER environment.", file=sys.stderr)
    class DummyLog:
        def info(self, msg): print(f"[INFO] {msg}")
        def warning(self, msg): print(f"[WARN] {msg}")
    class DummyEnv:
        log = DummyLog()
    env = DummyEnv()
# --- END: Core SNIPER Environment Integration ---

# Import the license generator and Rich UI components.
from .licenses import get_license_content
from rich.status import Status

def create_project(project_name, project_type, template_dir, variables, options, manifest, console):
    """
    The main project creation function. Handles file copying, template rendering, and command execution.
    
    Args:
        project_name (str): The name of the new project directory.
        project_type (str): The name of the template to use.
        template_dir (str): The path to the directory containing templates.
        variables (dict): Data for rendering Jinja2 templates.
        options (dict): User-selected options (e.g., git, docker).
        manifest (dict): The loaded 'sniper.json' for the selected template.
        console (rich.console.Console): The Rich console instance for UI elements.

    Returns:
        A tuple (success_bool, error_message_str).
    """
    source_dir = os.path.join(template_dir, project_type)

    if not os.path.isdir(source_dir):
        return False, f"Template '{project_type}' not found in '{template_dir}'."

    # --- Step 1: Handle Existing Directory ---
    if os.path.exists(project_name):
        env.log.warning(f"A directory named '{project_name}' already exists.")
        try:
            overwrite = questionary.confirm("Do you want to remove it and continue?", default=False).ask()
            if not overwrite:
                return False, "Operation cancelled by user."
            
            # Use rich.status for a clean, animated status message.
            with console.status(f"[bold yellow]Removing existing directory '{project_name}'...[/]") as status:
                shutil.rmtree(project_name)
        except (KeyboardInterrupt, TypeError):
            # Gracefully handle Ctrl+C during the confirmation prompt.
            return False, "Operation cancelled by user."

    # --- Step 2: Copy Template Files ---
    try:
        with console.status(f"[cyan]Copying template '{project_type}'...[/]") as status:
            shutil.copytree(source_dir, project_name, ignore=shutil.ignore_patterns('sniper.json'))
    except OSError as e:
        return False, f"Failed to copy template files: {e}"

    # --- Step 3: Conditional File Handling (e.g., Docker) ---
    if not options.get('docker', False):
        env.log.info("Skipping Docker setup as requested...")
        dockerfile_path = os.path.join(project_name, 'Dockerfile')
        compose_path = os.path.join(project_name, 'docker-compose.yml')
        if os.path.exists(dockerfile_path):
            os.remove(dockerfile_path)
        if os.path.exists(compose_path):
            os.remove(compose_path)

    # --- Step 4: Create LICENSE File ---
    license_type = options.get('license')
    if license_type:
        license_content = get_license_content(license_type, variables.get('author_name', ''))
        with open(os.path.join(project_name, 'LICENSE'), 'w', encoding='utf-8') as f:
            f.write(license_content.strip())
    
    # --- Step 5: Process All Files with Jinja2 Templating Engine ---
    env.log.info("Processing template files with Jinja2...")
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(project_name),
        autoescape=False,
        variable_start_string="{{", # Use double curly braces for variables
        variable_end_string="}}",
    )
    for root, _, files in os.walk(project_name):
        for filename in files:
            filepath = os.path.join(root, filename)
            # Use relative path for Jinja's loader
            template_path = os.path.relpath(filepath, project_name)
            try:
                template = jinja_env.get_template(template_path)
                rendered_content = template.render(variables)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(rendered_content)
            except (jinja2.exceptions.TemplateError, UnicodeDecodeError):
                # Silently ignore binary files or files that cause Jinja errors (e.g., images).
                pass
    
    # --- Step 6: Run Post-Initialization Commands ---
    # Handle Git initialization first, if requested.
    if options.get('git'):
        with console.status("[cyan]Initializing Git repository...[/]") as status:
            # Use the centralized env.run_command for consistency.
            result = env.run_command(['git', 'init', '-q'], cwd=project_name)
            if result.returncode != 0:
                env.log.warning(f"Failed to initialize Git repository. Git might not be installed or configured. Error: {result.stderr}")

    # Run commands defined in the template's 'sniper.json' manifest.
    for command_info in manifest.get('post_init_commands', []):
        cmd_template = command_info['command']
        # Render the command itself with variables (e.g., `go mod init {{project_name}}`)
        cmd = jinja2.Template(cmd_template).render(variables)
        message = command_info.get('message', f"Running '{cmd}'...")
        
        with console.status(f"[cyan]{message}[/]") as status:
            try:
                # Using shell=True is necessary for complex commands with operators like '&&' or '|'.
                # It should be used with trusted commands from the template manifests.
                subprocess.run(cmd, cwd=project_name, check=True, shell=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                # Provide detailed error feedback to the user if a command fails.
                error_details = e.stderr.strip() if e.stderr else e.stdout.strip()
                return False, f"Post-init command '{cmd}' failed:\n{error_details}"

    return True, None
