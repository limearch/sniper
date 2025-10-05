# project_init/core.py
import os
import sys
import shutil
import subprocess
from .licenses import get_license_content
from .utils import print_info, print_success, print_error, print_warn, Spinner

def create_project(project_name, project_type, template_dir, variables, options):
    source_dir = os.path.join(template_dir, project_type)
    
    if os.path.exists(project_name):
        print_error(f"A directory named '{project_name}' already exists.")
        return False

    with Spinner(f"Copying template '{project_type}'..."):
        try:
            shutil.copytree(source_dir, project_name)
        except OSError as e:
            print_error(f"Failed to copy template: {e}")
            return False

    # Handle optional files
    if not options.get('dockerfile'):
        dockerfile_path = os.path.join(project_name, 'Dockerfile')
        if os.path.exists(dockerfile_path): os.remove(dockerfile_path)
    
    license_path = os.path.join(project_name, 'LICENSE')
    if not options.get('license'):
        if os.path.exists(license_path): os.remove(license_path)
    else:
        variables['{{license_content}}'] = get_license_content(options['license'], variables.get('{{author_name}}', ''))
    
    print_info("Processing template files...")
    for root, _, files in os.walk(project_name):
        for filename in files:
            filepath = os.path.join(root, filename)
            process_file(filepath, variables)
    
    run_post_init_steps(project_name, project_type, options)
    return True

def process_file(filepath, variables):
    try:
        with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
        for var, value in variables.items(): content = content.replace(var, str(value))
        with open(filepath, 'w', encoding='utf-8') as f: f.write(content)
    except (UnicodeDecodeError, IOError): pass

def run_post_init_steps(project_name, project_type, options):
    project_path = os.path.abspath(project_name)
    
    if options.get('git'):
        with Spinner("Initializing Git repository..."):
            try:
                subprocess.run(['git', 'init', '-q'], cwd=project_path, check=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                print_warn("Could not initialize Git. Is Git installed and in your PATH?")
    
    if project_type == 'python':
        with Spinner("Creating Python virtual environment..."):
            try:
                subprocess.run([sys.executable, '-m', 'venv', '.venv'], cwd=project_path, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print_warn(f"Failed to create virtual environment: {e.stderr.decode('utf-8').strip()}")
    # ... Add logic for other project types ...

def print_summary(project_name, project_type):
    """Prints a final summary and next steps."""
    print_success(f"\nProject '{project_name}' created successfully!")
    print("\nNext steps:")
    print(f"  1. cd {project_name}")
    if project_type == 'python':
        print("  2. source .venv/bin/activate  (or .\\venv\\Scripts\\activate on Windows)")
        print("  3. # (Optional) pip install -r requirements.txt")
    elif project_type == 'nodejs':
        print("  2. npm install")
    print("\nHappy coding!")