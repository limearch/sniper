# File: project_init/cli.py (COMPLETE AND UPDATED)
# Description: The full CLI for sniper-init, with the Docker question added.

import os
import sys
import json
import argparse
import questionary
from datetime import datetime
import jinja2 # Import jinja2 here for the summary function

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.align import Align
except ImportError:
    print("\033[91m[ERROR]\033[0m The 'rich' library is required. Please run 'pip install rich'.")
    sys.exit(1)

from .config import load_config
from .core import create_project
from .utils import Colors

console = Console()

def get_available_templates(templates_dirs):
    """Scans template directories and returns a unique, sorted list of templates."""
    templates = set()
    for dir_path in templates_dirs:
        if dir_path and os.path.isdir(dir_path):
            templates.update([d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))])
    return sorted(list(templates))

def load_template_manifest(template_name, templates_dirs):
    """Loads the sniper.json manifest for a given template."""
    for dir_path in templates_dirs:
        manifest_path = os.path.join(dir_path, template_name, 'sniper.json')
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"{Colors.RED}[ERROR]{Colors.ENDC} Invalid JSON in manifest: {manifest_path}")
    return {}

def show_rich_help(available_templates):
    """Displays the new, multi-panel, rich-formatted help screen embodying the SNIPER style."""
    console.print(Panel(Text("SNIPER: Project Initializer", style="bold magenta", justify="center"),
                  subtitle="[grey50]v0.3.0[/grey50]", border_style="magenta"))

    philosophy_text = Text.from_markup("Bootstrap new software projects from powerful, dynamic templates. Built on the SNIPER philosophy of [bold]precision, speed, and integration[/bold].")
    console.print(Panel(philosophy_text, title="[cyan]Philosophy[/]", border_style="cyan"))

    usage_text = f"""
[bold]Interactive Mode (Recommended):[/]
  [yellow]sniper-init[/]
[bold]Direct Mode:[/b]
  [yellow]sniper-init[/] [cyan]<PROJECT_NAME>[/] [green]-t <TEMPLATE>[/] [green][OPTIONS][/]
[bold]Options:[/b]
  [green]-t, --template <T>[/]   Specify the project template to use.
                     [dim]Available: {', '.join(available_templates) or 'None'}[/]
  [green]--no-git[/]           Do not initialize a Git repository.
  [green]--with-docker[/]      Force inclusion of Docker files.
  [green]--no-docker[/]        Force exclusion of Docker files.
  [green]-h, --help[/]            Show this help message.
"""
    console.print(Panel(Text.from_markup(usage_text.strip()), title="[blue]Usage & Options[/]", border_style="blue"))
    
    templates_guide = "Each template is a directory containing a `sniper.json` manifest file which defines dynamic questions, post-init commands, and next steps, making the tool incredibly extensible."
    console.print(Panel(Text.from_markup(templates_guide.strip()), title="[yellow]Template System[/]", border_style="yellow"))
    sys.exit(0)

def print_rich_summary(name, template, manifest, variables):
    """Displays a beautiful, partitioned summary panel after project creation."""
    console.print()
    summary_table = Table(box=None, show_header=False, expand=True)
    summary_table.add_column("Property", style="bold magenta", justify="right", width=15)
    summary_table.add_column("Value", style="cyan")
    summary_table.add_row("Project Name", name)
    summary_table.add_row("Template", template)
    summary_table.add_row("Location", os.path.abspath(name))
    summary_table.add_row("Created On", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    next_steps_text = Text("\n")
    steps = manifest.get('next_steps', [f"cd {name}"])
    for i, step in enumerate(steps, 1):
        rendered_step = jinja2.Template(step).render(variables)
        next_steps_text.append(f"  {i}. {rendered_step}\n", style="default")
    
    console.print(Panel(summary_table, title="[bold green]✅ Project Created Successfully[/]", border_style="green"))
    console.print(Panel(Align.left(next_steps_text), title="[bold yellow]Next Steps[/]", border_style="yellow"))
    console.print(Align.center(Text("Happy Coding!", style="bold magenta")))

def main():
    """Main entry point for the new sniper-init command."""
    config = load_config()
    package_dir = os.path.dirname(os.path.abspath(__file__))
    default_templates_dir = os.path.join(package_dir, '..', 'templates')
    custom_templates_dir = config.get('custom_templates_dir')
    templates_dirs = [default_templates_dir, custom_templates_dir]
    available_templates = get_available_templates(templates_dirs)

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

    variables = {
        "author_name": config.get('author_name', 'Your Name'),
        "author_email": config.get('author_email', 'your@email.com'),
        "year": datetime.now().year
    }
    options = {}

    try:
        if not args.name:
            # --- Interactive Mode ---
            console.print(Panel(Text("SNIPER: Interactive Project Setup", style="bold magenta", justify="center")))
            name = questionary.text("Project name:").ask()
            if not name: return

            template = questionary.select("Project type:", choices=available_templates).ask()
            if not template: return

            manifest = load_template_manifest(template, templates_dirs)
            for question in manifest.get('questions', []):
                answer = questionary.text(question['prompt'], default=str(question.get('default', ''))).ask()
                variables[question['key']] = answer

            git = questionary.confirm("Initialize Git repository?", default=True).ask()
            docker = questionary.confirm("Include Docker files?", default=True).ask()
            license_choice = questionary.select("Choose a license:", choices=['None', 'MIT', 'Apache 2.0'], default='MIT').ask()
            options = {'git': git, 'docker': docker, 'license': license_choice if license_choice != 'None' else None}
        else:
            # --- Direct Mode ---
            if not args.template:
                print(f"{Colors.RED}[ERROR]{Colors.ENDC} Template must be specified with '-t' in direct mode.")
                sys.exit(1)
            name = args.name
            template = args.template
            manifest = load_template_manifest(template, templates_dirs)
            for question in manifest.get('questions', []):
                variables[question['key']] = question.get('default', '')
            
            docker_option = True if args.docker is None else args.docker
            options = {'git': args.git, 'docker': docker_option, 'license': 'MIT'}
    except (KeyboardInterrupt, TypeError):
        console.print("\n[bold yellow]Operation cancelled by user.[/]")
        return

    variables.update({"project_name": name, "project_type": template})
    template_dir = custom_templates_dir if custom_templates_dir and os.path.exists(os.path.join(custom_templates_dir, template)) else default_templates_dir
    
    success, error = create_project(name, template, template_dir, variables, options, manifest)

    if success:
        print_rich_summary(name, template, manifest, variables)
    else:
        console.print(f"\n[bold red]Error during project creation:[/]\n{error}")
        sys.exit(1)