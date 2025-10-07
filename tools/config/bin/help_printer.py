# help_printer.py
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    print("Error: The 'rich' library is required for the help screen. Run: pip install rich")
    sys.exit(1)

def show_configer_help(prog_name="configer"):
    """Displays the custom, rich-formatted help screen for the configer tool."""
    
    console = Console()
    
    title = Text("SNIPER: Config Manager", style="bold magenta", justify="center")
    
    usage = Text.from_markup(
        f"[bold]Usage:[/] [yellow]{prog_name}[/] [green]<COMMAND>[/] [cyan]<category>[/] [cyan]<key>[/] [cyan][value][/]"
    )
    
    main_panel_text = """
[bold]Description:[/b]
  A command-line tool to securely manage the main `sniper-config.json`
  file. It allows setting, retrieving, and deleting key-value pairs
  organized by category.
"""

    commands_text = """
[bold]Commands:[/b]
  [green]set <category> <key> <value>[/]    Set or update a configuration value.
  [green]get <category> <key>[/]            Retrieve a specific value.
  [green]delete <category> <key>[/]         Delete a key-value pair.
  [green]help[/]                             Show this help message.
"""

    examples_text = """
[bold]Examples:[/b]
  [#] Set the default username for API tools
  [yellow]configer set api username my_user[/]

  [#] Retrieve the username
  [yellow]configer get api username[/]

  [#] Set a complex value with spaces
  [yellow]configer set prompt welcome_message "Welcome back, Operator"[/]
"""
    
    console.print(Panel(title, border_style="magenta", padding=(0, 1)))
    console.print(usage, justify="center")
    console.print(Panel(Text.from_markup(main_panel_text.strip()), title="Overview", border_style="blue"))
    console.print(Panel(Text.from_markup(commands_text.strip()), title="Commands", border_style="cyan"))
    console.print(Panel(Text.from_markup(examples_text.strip()), title="Examples", border_style="green"))
    sys.exit(0)

if __name__ == "__main__":
    prog_name_arg = sys.argv[1] if len(sys.argv) > 1 else "configer"
    show_configer_help()
