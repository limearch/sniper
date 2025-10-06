#!/usr/bin/env python3

import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.align import Align
except ImportError:
    print("Error: The 'rich' library is required to display this help message.")
    print("Please install it using: pip install rich")
    sys.exit(1)

def display_main_help():
    """
    Displays the main, rich-formatted help screen for the SNIPER CLI TOOL.
    """
    console = Console()

    # --- Header ---
    # Centered alignment for the main title
    header_text = Align.center(Text("SNIPER CLI TOOL", style="bold magenta"))
    console.print(Panel(header_text, border_style="magenta", expand=True, padding=(1, 0)))

    # --- NEW: About Section ---
    about_text = """
[bold]SNIPER[/] is a comprehensive command-line environment designed to supercharge your terminal.
It bundles a powerful suite of integrated tools, shortcuts, and utilities to streamline workflows for developers, penetration testers, and security enthusiasts.
"""
    console.print(Panel(Text.from_markup(about_text.strip()), title="[cyan]About SNIPER[/]", border_style="cyan", padding=1))

    # --- Sections ---
    
    # 1. Shortcuts (Aliases for fast access)
    shortcuts = [
        "[green]c[/]      - Clear screen",
        "[green]m[/]      - Micro text editor",
        "[green]n[/]      - Nano text editor",
        "[green]gc[/]     - Git clone",
        "[green]ls[/]     - List all files (ls -a)",
        "[green]l[/]      - List files formatted (ls -CF)",
        "[green]mk[/]     - Make a new folder",
        "[green]tu[/]     - Create a new empty file (touch)",
        "[green]cdsd[/]   - Change directory to sdcard",
        "[green]cddo[/]   - Change directory to Downloads",
    ]
    console.print(Panel(Columns(shortcuts, equal=True, expand=True), title="[bold yellow]❯ Shortcuts[/]", border_style="yellow", subtitle="Shell Aliases"))

    # 2. Development & Productivity Tools
    dev_tools = [
        "[green]compress[/]      - Compress files and folders into various formats (zip, tar).",
        "[green]format[/]        - Auto-format source code files (JSON, Python, etc.).",
        "[green]sniper-init[/]   - Initialize new project structures for Python, Node.js, and more.",
        "[green]combinde[/]      - Combine a project's source files into a single text file for AI models.",
        "[green]run[/]           - A universal runner for executing files from any programming language.",
        "[green]lib-installer[/] - A simplified installer for Python libraries.",
    ]
    console.print(Panel(Columns(dev_tools, equal=True, expand=True), title="[bold blue]❯ Development & Productivity Tools[/]", border_style="blue"))

    # 3. Network & Reconnaissance Tools
    net_tools = [
        "[green]fastfind[/]      - An advanced, multi-threaded tool to find files and folders.",
        "[green]social_devs[/]   - Search for a username across various social media sites.",
        "[green]net-discover[/]  - Get details about your network and discover connected devices.",
        "[green]site-crafter[/]        - Download entire web pages or websites for offline analysis.",
        "[green]iplookup[/]      - Get geographic and network information about an IP address or domain.",
        "[green]listen[/]        - Listen on a network port or create a temporary local web server.",
        "[green]scan[/]          - A fast, concurrent port scanner to check for open ports.",
    ]
    console.print(Panel(Columns(net_tools, equal=True, expand=True), title="[bold green]❯ Network & Reconnaissance Tools[/]", border_style="green"))

    # 4. File & System Utilities
    utils_commands = [
        "[green]size[/]          - Display the size of a file or folder.",
        "[green]file-info[/]     - Show detailed metadata and information about files.",
        "[green]timer[/]         - Execute any command with a specified timeout.",
        "[green]lsmap[/]         - Visualize the file and folder structure as an interactive tree.",
        "[green]view-source[/]   - Display source code with syntax highlighting in the terminal.",
        "[green]text-image[/]    - Convert any image into ASCII art.",
        "[green]sniper-crypt[/]  - A powerful tool to encrypt and decrypt any file securely.",
        "[green]shall-game[/]    - A simple shell game for entertainment.",
    ]
    console.print(Panel(Columns(utils_commands, equal=True, expand=True), title="[bold cyan]❯ File & System Utilities[/]", border_style="cyan"))
    
    # 5. Unavailable / In-Development Tools
    unavailable = [
        "[grey50]ARGUS[/]          - Payload and virus injection framework.",
        "[grey50]pyprivate[/]      - Encrypt Python source code files.",
        "[grey50]chmac[/]           - A utility to change your device's MAC address.",
    ]
    console.print(Panel(Columns(unavailable, equal=True, expand=True), title="[bold grey50]❯ In Development[/]", border_style="grey50", subtitle="Coming Soon"))

    # --- NEW: Troubleshooting Section ---
    troubleshooting_text = """
• [bold red]Command not found[/]: Ensure the SNIPER activation script has been sourced correctly and the tool's 'bin' directories are in your [cyan]$PATH[/].
• [bold red]Missing Dependencies[/]: Some tools depend on external libraries (like [cyan]rich[/], [cyan]nmap[/], [cyan]shfmt[/]). If a tool fails, check its specific help ([yellow]readme <tool>[/]) for a list of dependencies.
• [bold red]Permission Denied[/]: Some tools, like [cyan]scan[/] or [cyan]net-discover[/], may require elevated privileges to function correctly.
"""
    console.print(Panel(Text.from_markup(troubleshooting_text.strip()), title="[bold red]⚠️ Troubleshooting & Common Errors[/]", border_style="red"))

    # --- Footer / System Commands ---
    system_footer = """
[bold]System Commands:[/b]
  [green]readme[/]              - Displays this main help screen.
  [green]readme <tool>[/]      - Get detailed help for a specific tool (e.g., [yellow]readme scan[/]).
  [green]exit[/]                - Stop the SNIPER tool and restore the original shell environment.
"""
    console.print(Panel(Text.from_markup(system_footer.strip()), title="[bold]System & Help[/]", border_style="white"))


if __name__ == "__main__":
    display_main_help()

