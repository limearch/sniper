# help_printer.py
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    # This should ideally not be reached because the C code checks first,
    # but it's a good safeguard.
    print("Error: The 'rich' library is required. Please run: pip install rich")
    sys.exit(1)

def show_fastfind_help(prog_name="fastfind"):
    """Displays the custom, rich-formatted help screen for fastfind."""
    
    console = Console()
    
    title = Text("SNIPER: fastfind - Advanced Directory Walker", style="bold magenta", justify="center")
    
    usage = Text.from_markup(
        f"[bold]Usage:[/] [yellow]{prog_name}[/] [cyan]-p <regex>[/] [cyan][directory][/] [green][OPTIONS][/]"
    )
    
    filtering_panel_text = """
[bold]Filtering & Matching:[/b]
  [green]-p, --pattern <regex>[/]      (Required) Regex to match filenames.
  [green]-d, --directory <path>[/]      Directory to start from (Default: .).
  [green]-e, --ext <extension>[/]       Filter by file extension (e.g., 'py').
  [green]-t, --type <f|d|l>[/]          Filter by type: file (f), directory (d), or link (l).
  [green]--size <[+|-]N[K|M|G]>[/] Filter by size (e.g., +10M, -1K, 0).
  [green]--mtime <[+|-]Nd>[/]      Filter by modification time in days (e.g., -7d, +30d).
  [green]--owner <user>[/]         Filter by file owner (e.g., 'root').
  [green]--perms <octal>[/]        Filter by exact permissions (e.g., '755').
  [green]--content <regex>[/]      Search inside file contents for a regex match.
  [green]--with-line-number <regex>[/]      Search inside file contents and show line.
"""

    behavior_panel_text = """
[bold]Behavior:[/b]
  [green]-i, --ignore-case[/]          Enable case-insensitive matching.
  [green]--no-hidden[/]             Ignore hidden files and directories (default).
  [green]--ignore-vcs[/]            Automatically ignore files from .gitignore (default).
  [green]--no-ignore[/]             Disable all ignore-file logic.
  [green]-m, --max-depth <N>[/]        Search N levels deep (-1 for unlimited).
  [green]--exclude <dir>[/]        Exclude a directory by name (can be used multiple times).
"""
    
    actions_panel_text = """
[bold]Actions & Output:[/b]
  [green]--exec <cmd>[/]           Execute a command on each result. Use `{}` for the path.
  [green]--delete[/]                Delete found files and directories.
  [green]-l, --long-listing[/]         Use a long listing format with extra details.
  [green]--format <text|json|csv>[/] Change the output format.
  [green]-o, --output <file>[/]        Write output to a file instead of stdout.
"""

    console.print(Panel(title, border_style="magenta", padding=(0, 1)))
    console.print(usage, justify="center")
    console.print(Panel(Text.from_markup(filtering_panel_text.strip()), title="Filtering & Matching", border_style="blue"))
    console.print(Panel(Text.from_markup(behavior_panel_text.strip()), title="Behavior", border_style="cyan"))
    console.print(Panel(Text.from_markup(actions_panel_text.strip()), title="Actions & Output", border_style="green"))

if __name__ == "__main__":
    # Get the program name from the command-line argument
    prog_name_arg = sys.argv[1] if len(sys.argv) > 1 else "fastfind"
    show_fastfind_help()
