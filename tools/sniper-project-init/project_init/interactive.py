# project_init/interactive.py
import os
import questionary
from .core import Colors, create_project
from .config import load_config

def get_available_templates(templates_dirs):
    """Scans template directories and returns a list of choices."""
    templates = {}
    for dir_path in templates_dirs:
        if os.path.isdir(dir_path):
            for t_name in os.listdir(dir_path):
                if os.path.isdir(os.path.join(dir_path, t_name)):
                    if t_name not in templates:
                        templates[t_name] = os.path.join(dir_path, t_name)
    return list(templates.keys())

def start_interactive_session():
    """Runs the main interactive CLI session."""
    config = load_config()
    
    # Define template locations
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_templates_dir = os.path.join(script_dir, 'templates')
    custom_templates_dir = config.get('custom_templates_dir')
    template_choices = get_available_templates([default_templates_dir, custom_templates_dir])

    if not template_choices:
        print(f"{Colors.RED}[ERROR]{Colors.ENDC} No templates found.")
        return

    print(f"{Colors.GREEN}--- SNIPER Project Initializer ---{Colors.ENDC}\n")

    project_name = questionary.text("Project name:").ask()
    if not project_name: return

    project_type = questionary.select("Project type:", choices=template_choices).ask()
    if not project_type: return

    # Optional features
    options = {
        'git': questionary.confirm("Initialize Git repository?", default=True).ask(),
        'dockerfile': questionary.confirm("Include a Dockerfile?", default=False).ask(),
        'license': questionary.select(
            "Choose a license:", 
            choices=['None', 'MIT', 'Apache 2.0', 'GPLv3'], 
            default='None'
        ).ask()
    }
    if options['license'] == 'None':
        options['license'] = None

    # Variables for template processing
    variables = {
        "{{project_name}}": project_name,
        "{{project_type}}": project_type,
        "{{author_name}}": config.get('author_name', ''),
        "{{author_email}}": config.get('author_email', '')
    }

    # Determine which template directory to use
    template_dir_to_use = custom_templates_dir if custom_templates_dir and os.path.exists(os.path.join(custom_templates_dir, project_type)) else default_templates_dir

    if create_project(project_name, project_type, template_dir_to_use, variables, options):
        # (Print success message and next steps here)
        print_success(f"\nProject '{project_name}' created successfully!")