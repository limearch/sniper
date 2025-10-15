# File: tools/py-shroud/engine/utils.py (Final Corrected Version)
# Description: Shared utility functions for colored output and final reporting.

import sys
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

# --- START: CORE FIX for rich compatibility ---
# Standard console for stdout
console = Console()
# A separate console instance specifically for stderr output
console_err = Console(file=sys.stderr)
# --- END: CORE FIX ---




def print_final_report(stats: dict):
    """Displays a rich, formatted table summarizing the obfuscation process."""
    
    original_size_kb = stats.get('original_size', 0) / 1024
    final_size_kb = stats.get('final_size', 0) / 1024
    time_taken = stats.get('end_time', 0) - stats.get('start_time', 0)
    
    size_change = final_size_kb - original_size_kb
    size_change_percent = (size_change / original_size_kb * 100) if original_size_kb > 0 else 0
    
    if size_change > 0:
        size_change_str = f"[yellow]{size_change:+.2f} KB ({size_change_percent:+.1f}%)[/yellow]"
    else:
        size_change_str = f"[green]{size_change:+.2f} KB ({size_change_percent:+.1f}%)[/green]"

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="bold cyan", justify="right")
    table.add_column("Value", style="white")

    table.add_row("Input File:", stats.get('input_file', 'N/A'))
    table.add_row("Output File:", stats.get('output_file', 'N/A'))
    table.add_row("-" * 20, "-" * 30)
    table.add_row("Obfuscation Level:", f"[bold magenta]Level {stats.get('level', 'N/A')}[/bold magenta]")
    table.add_row("Names Mangled:", str(stats.get('names_mangled', '0')))
    table.add_row("Strings Encrypted:", str(stats.get('strings_encrypted', '0')))
    table.add_row("-" * 20, "-" * 30)
    table.add_row("Original Size:", f"{original_size_kb:.2f} KB")
    table.add_row("Final Size:", f"{final_size_kb:.2f} KB")
    table.add_row("Size Change:", Text.from_markup(size_change_str))
    table.add_row("Time Taken:", f"{time_taken:.3f} seconds")

    console.print(Panel(
        table,
        title="[bold magenta]py-shroud Operation Report[/]",
        border_style="green",
        expand=False
    ))
    