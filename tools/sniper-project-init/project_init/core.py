# File: project_init/core.py (COMPLETE AND UPDATED)
# Description: Handles pre-existing directories, and conditionally removes Docker files.

import os
import shutil
import subprocess
import jinja2
import questionary

from .licenses import get_license_content
from .utils import print_info, print_warn, Spinner

def create_project(project_name, project_type, template_dir, variables, options, manifest):
    """
    The main project creation function. Returns (success_bool, error_message_str).
    """
    source_dir = os.path.join(template_dir, project_type)

    if not os.path.isdir(source_dir):
        return False, f"Template '{project_type}' not found."

    # --- NEW: Handle existing directory ---
    if os.path.exists(project_name):
        print_warn(f"A directory named '{project_name}' already exists.")
        try:
            # Use a direct questionary call here for user interaction within the core logic.
            overwrite = questionary.confirm("Do you want to remove it and continue?", default=False).ask()
            if not overwrite:
                return False, "Operation cancelled by user."
            with Spinner(f"Removing existing directory '{project_name}'..."):
                shutil.rmtree(project_name)
        except (KeyboardInterrupt, TypeError):
            # Handles Ctrl+C or if questionary is not available in a pipe
            return False, "Operation cancelled by user."

    # 1. Copy template files
    try:
        with Spinner(f"Copying template '{project_type}'..."):
            shutil.copytree(source_dir, project_name, ignore=shutil.ignore_patterns('sniper.json'))
    except OSError as e:
        return False, f"Failed to copy template: {e}"

    # 2. Conditionally remove Docker files based on user option
    if not options.get('docker', False):
        print_info("Skipping Docker setup as requested...")
        dockerfile_path = os.path.join(project_name, 'Dockerfile')
        compose_path = os.path.join(project_name, 'docker-compose.yml')
        if os.path.exists(dockerfile_path):
            os.remove(dockerfile_path)
        if os.path.exists(compose_path):
            os.remove(compose_path)

    # 3. Handle LICENSE file creation
    license_type = options.get('license')
    if license_type:
        license_content = get_license_content(license_type, variables.get('author_name', ''))
        with open(os.path.join(project_name, 'LICENSE'), 'w', encoding='utf-8') as f:
            f.write(license_content.strip())
    
    # 4. Process all files in the new project directory with Jinja2
    print_info("Processing template files...")
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(project_name),
        autoescape=False,
        variable_start_string="{{",
        variable_end_string="}}",
    )
    for root, _, files in os.walk(project_name):
        for filename in files:
            filepath = os.path.join(root, filename)
            template_path = os.path.relpath(filepath, project_name)
            try:
                template = jinja_env.get_template(template_path)
                rendered_content = template.render(variables)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(rendered_content)
            except (jinja2.exceptions.TemplateError, UnicodeDecodeError):
                # Ignore binary files or files that cause Jinja errors
                pass
    
    # 5. Run post-initialization commands from sniper.json
    # Git initialization is handled first if requested
    if options.get('git'):
        with Spinner("Initializing Git repository..."):
            subprocess.run(['git', 'init', '-q'], cwd=project_name, check=False)

    for command_info in manifest.get('post_init_commands', []):
        cmd_template = command_info['command']
        # Render the command itself with variables (e.g., `go mod init {{project_name}}`)
        cmd = jinja2.Template(cmd_template).render(variables)
        message = command_info.get('message', f"Running '{cmd}'...")
        
        with Spinner(message):
            try:
                subprocess.run(cmd, cwd=project_name, check=True, shell=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                # Provide detailed error feedback to the user
                error_details = e.stderr.strip() if e.stderr else e.stdout.strip()
                return False, f"Command '{cmd}' failed:\n{error_details}"

    return True, None