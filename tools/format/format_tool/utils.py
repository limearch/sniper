# format_tool/utils.py
import shutil
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# --- Dependency Check ---
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    rich_available = True
except ImportError:
    rich_available = False

def check_command_exists(command):
    """Checks if a command (like 'shfmt') exists in the system's PATH."""
    return shutil.which(command) is not None

def show_rich_help():
    """Displays the custom, rich-formatted help screen for the format tool."""
    if not rich_available:
        print("Error: 'rich' library is required for the help screen. Run: pip install rich")
        sys.exit(1)
        
    console = Console()
    title = Text("SNIPER: format - Universal Code Formatter", style="bold magenta", justify="center")
    
    usage = Text.from_markup(
        "[bold]Usage:[/] [yellow]format[/] [cyan]<PATH>[/] [green][OPTIONS][/]"
    )
    
    main_panel_text = """
[bold]Description:[/b]
  A powerful tool to automatically format source code files and
  directories. It supports multiple languages by leveraging dedicated
  formatters and external command-line tools.

[bold]Arguments:[/b]
  [cyan]<PATH>[/]               The file or directory to format.

[bold]Options:[/b]
  [green]-h, --help[/]         Show this help message and exit.
  [green]-v, --verbose[/]      Enable verbose output to see which files are processed.
"""

    behavior_panel_text = """
[bold]Behavior & Filtering:[/b]
  [green]-s, --spaces <N>[/]    Number of spaces for indentation (default: 4).
  [green]-r, --recursive[/]    Recursively format files in a directory (default).
  [green]-b, --backup[/]       Create a '.bak' backup of each file before formatting.
  [green]-f, --filter <.ext>[/] Only format files with these extensions (e.g., [cyan]-f .py .js[/]).
"""

    advanced_panel_text = """
[bold]Advanced Features:[/b]
  [green]-c, --check[/]        'Check mode'. Don't modify files, just report which ones
                     need formatting and exit with a non-zero code if any do.
                     Ideal for CI/CD pipelines.
  [green]-p, --parallel[/]   Enable parallel processing to format multiple files at
                     once, significantly speeding up large projects.
"""

    examples_text = """
[bold]Examples:[/b]
  [#] Format a single python file with 2-space indents
  [yellow]format[/] [cyan]my_script.py[/] [green]-s 2[/]

  [#] Recursively format an entire project and create backups
  [yellow]format[/] [cyan]./my_project/[/] [green]-b -v[/]

  [#] Check if any .js or .css files in a directory need formatting
  [yellow]format[/] [cyan]assets/[/] [green]--check -f .js .css[/]
"""
    
    console.print(Panel(title, border_style="magenta", padding=(0, 1)))
    console.print(usage, justify="center")
    console.print(Panel(Text.from_markup(main_panel_text.strip()), title="Overview", border_style="blue"))
    console.print(Panel(Text.from_markup(behavior_panel_text.strip()), title="Behavior", border_style="cyan"))
    console.print(Panel(Text.from_markup(advanced_panel_text.strip()), title="Advanced", border_style="green"))
    console.print(Panel(Text.from_markup(examples_text.strip()), title="Examples", border_style="yellow"))
    