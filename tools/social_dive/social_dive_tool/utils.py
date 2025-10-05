# social_dive_tool/utils.py
import json
from pathlib import Path
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    print("Error: The 'rich' library is required. Please run: pip install rich")
    sys.exit(1)

# --- UPDATED: Rich Help Screen Function ---
def show_rich_help():
    """Displays the custom, rich-formatted help screen for social-dive."""
    console = Console()
    title = Text("SNIPER: social-dive - OSINT Username Checker", style="bold magenta", justify="center")
    
    usage = Text.from_markup(
        "[bold]Usage:[/] [yellow]social-dive[/] [cyan]<USERNAME>[/] [green][OPTIONS][/]"
    )
    
    main_panel_text = """
[bold]Description:[/b]
  A fast, multi-threaded OSINT tool that checks for the existence
  of a specific username across a wide range of websites and social networks.

[bold]Arguments:[/b]
  [cyan]<USERNAME>[/]           The username to search for.

[bold]Options:[/b]
  [green]-h, --help[/]             Show this help message and exit.
  [green]-o, --output <FILE>[/]   Export results to a file (formats: txt, csv, json).
  [green]-c, --category <CAT>[/]  Search only within a specific category.
  [green]--list-categories[/]     List all available site categories and exit.
  [green]-p, --proxy <URL>[/]       Use a proxy for requests (e.g., http://127.0.0.1:8080).
  [green]-t, --timeout <SEC>[/]     Set request timeout in seconds (default: 10).
"""

    examples_text = """
[bold]Examples:[/b]
  [#] Perform a standard search for a username
  [yellow]social-dive[/] [cyan]johndoe[/]

  [#] Search only in 'Gaming' sites and save results to a CSV file
  [yellow]social-dive[/] [cyan]mastergamer[/] [green]-c Gaming -o results.csv[/]

  [#] List all searchable categories
  [yellow]social-dive[/] [green]--list-categories[/]
"""

    # --- NEW: Disclaimer / False Positives Section ---
    disclaimer_text = """
[bold]Important Note on Accuracy:[/b]
  This tool checks for usernames based on server responses (like status
  codes or page content). However, many modern websites no longer
  provide clear "not found" errors to protect user privacy.

  Instead, they might redirect to a homepage or show a generic page,
  which can be misinterpreted by the tool as a valid user profile.

  [bold yellow]⚠️ Be Aware:[/] This can lead to [bold]"False Positives"[/] (reporting a
  profile that doesn't actually exist). Always manually verify the links
  for important results. This is an inherent limitation of automated
  username checking tools.
"""

    dependencies_text = """
[bold]Dependencies:[/b]
  - [cyan]requests[/]: For making HTTP requests.
  - [cyan]rich[/]: For displaying beautiful output.
"""
    
    console.print(Panel(title, border_style="magenta", padding=(0, 1)))
    console.print(usage, justify="center")
    console.print(Panel(Text.from_markup(main_panel_text.strip()), title="Overview & Options", border_style="blue"))
    console.print(Panel(Text.from_markup(examples_text.strip()), title="Examples", border_style="green"))
    console.print(Panel(Text.from_markup(dependencies_text.strip()), title="Dependencies", border_style="cyan"))
    
    # --- ADDED the new panel here ---
    console.print(Panel(Text.from_markup(disclaimer_text.strip()), title="[bold yellow]⚠️ Accuracy & False Positives[/]", border_style="yellow"))
    
    sys.exit(0)


def get_categories():
    """Reads data.json and returns a set of unique, sorted site categories."""
    try:
        data_file_path = Path(__file__).parent / "data.json"
        with open(data_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categories = set(info.get("category", "Uncategorized").capitalize() for info in data.values())
        return sorted(list(categories))
    except FileNotFoundError:
        return ["Error: data.json not found"]
