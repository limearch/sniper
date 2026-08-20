# File: tools/shatter/shatter_tool/ui.py
import time
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live

class ShatterUI:
    def __init__(self, console: Console, filename: str):
        self.console = console
        self.filename = filename
        self.start_time = time.time()
        self.hashes_processed = 0
        self.current_word = "Initializing..."
        self.found_password = None
        self.finished = False

    def update(self, count, word_ptr):
        """
        Callback method to be called from C++.
        """
        self.hashes_processed = count
        if word_ptr:
            try:
                # Decode bytes to string, replace errors to avoid crash
                self.current_word = word_ptr.decode('utf-8', errors='replace')
            except:
                self.current_word = "..."

    def get_renderable(self):
        """
        Generates the Rich renderable object (Panel).
        """
        current_time = time.time()
        elapsed = current_time - self.start_time
        if elapsed < 0.1: elapsed = 0.1 # Avoid division by zero
        
        speed = self.hashes_processed / elapsed

        # --- 1. Header Title ---
        title = Text("SNIPER :: SHATTER ENGINE", style="bold magenta")
        
        # --- 2. Stats Grid ---
        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)
        
        # Format speed nicely
        if speed > 1_000_000_000:
            spd_str = f"{speed/1_000_000_000:.2f} GH/s"
        elif speed > 1_000_000:
            spd_str = f"{speed/1_000_000:.2f} MH/s"
        elif speed > 1_000:
            spd_str = f"{speed/1_000:.2f} KH/s"
        else:
            spd_str = f"{speed:.0f} H/s"

        grid.add_row(
            f"[cyan]Target File:[/cyan] [white]{self.filename}[/white]",
            f"[cyan]Speed:[/cyan] [bold yellow]{spd_str}[/bold yellow]"
        )
        grid.add_row(
            f"[cyan]Attempts:[/cyan]  [white]{self.hashes_processed:,}[/white]",
            f"[cyan]Elapsed:[/cyan]  [white]{int(elapsed)}s[/white]"
        )

        # --- 3. Dynamic Status Section ---
        status_text = Text()
        status_text.append("\nStatus: ", style="dim white")
        
        if self.found_password:
            # Success State (Green)
            status_text.append("CRACKED SUCCESSFULLY\n", style="bold green")
            status_text.append("Password: ", style="white")
            status_text.append(f" {self.found_password} ", style="bold black on green")
        else:
            # Running State (Red)
            status_text.append("RUNNING\n", style="bold blue")
            status_text.append("Testing:  ", style="white")
            
            # Truncate word if too long
            display_word = self.current_word
            if len(display_word) > 25:
                display_word = display_word[:25] + "..."
                
            status_text.append(f"{display_word}", style="bold red reverse")

        # Combine into Panel
        panel = Panel(
            Group(grid, status_text),
            title=title,
            border_style="cyan" if not self.found_password else "green",
            padding=(1, 2)
        )
        return panel
