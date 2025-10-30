# File: tools/file-info/file_info_tool/core.py (REFACTORED)

import os
import sys
import json
import time
import stat
import hashlib
from pathlib import Path

# --- START: Core Integration ---
# This module is now imported by the entrypoint, which has already set up the path.
# We can directly import the environment.
try:
    from lib.sniper_env import env
except ImportError:
    # This fallback is for scenarios where the module might be tested in isolation.
    print("\033[91m[CRITICAL ERROR]\033[0m Could not import SNIPER environment.", file=sys.stderr)
    class DummyLog:
        def error(self, msg): print(f"[ERROR] {msg}", file=sys.stderr)
    class DummyEnv:
        log = DummyLog()
    env = DummyEnv()
# --- END: Core Integration ---

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.align import Align
except ImportError:
    env.log.critical("The 'rich' library is required. Please run: pip install rich")
    sys.exit(1)

console = Console()

class FileAnalyzer:
    def __init__(self):
        self.extensions_data = self._load_extensions()

    def _load_extensions(self):
        """Loads extension data from the JSON file."""
        try:
            data_file_path = Path(__file__).parent / "data" / "extensions.json"
            with open(data_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # --- CORE CHANGE: Use logger for warnings ---
            env.log.warning(f"Could not load extensions data: {e}")
            return {}

    # ... (get_formatted_size, get_permissions, calculate_hashes methods remain unchanged) ...
    def get_formatted_size(self, size_bytes):
        """Converts size in bytes to a human-readable format."""
        if size_bytes is None: return "N/A"
        if size_bytes < 1024: return f"{size_bytes} B"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:3.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def get_permissions(self, mode):
        """Converts stat mode to a human-readable permission string."""
        perms = ""
        perms += "r" if mode & stat.S_IRUSR else "-"
        perms += "w" if mode & stat.S_IWUSR else "-"
        perms += "x" if mode & stat.S_IXUSR else "-"
        perms += "r" if mode & stat.S_IRGRP else "-"
        perms += "w" if mode & stat.S_IWGRP else "-"
        perms += "x" if mode & stat.S_IXGRP else "-"
        perms += "r" if mode & stat.S_IROTH else "-"
        perms += "w" if mode & stat.S_IWOTH else "-"
        perms += "x" if mode & stat.S_IXOTH else "-"
        return perms
    
    def calculate_hashes(self, file_path):
        """Calculates MD5, SHA1, and SHA256 hashes for a file."""
        hashes = {}
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                hashes['md5'] = hashlib.md5(data).hexdigest()
                hashes['sha1'] = hashlib.sha1(data).hexdigest()
                hashes['sha256'] = hashlib.sha256(data).hexdigest()
            return hashes
        except Exception:
            return None


    def analyze(self, path_str):
        """Analyzes a file or directory and displays the information."""
        path = Path(path_str)
        if not path.exists():
            # --- CORE CHANGE: Use logger for errors ---
            env.log.error(f"Path '{path_str}' does not exist.")
            return

        try:
            file_stats = path.stat()
            is_dir = path.is_dir()
            
            # --- Panel 1: Basic Information ---
            basic_info_table = Table(box=None, show_header=False, expand=True)
            basic_info_table.add_column("Property", style="bold magenta", justify="right", width=20)
            basic_info_table.add_column("Value", style="green")

            ext = path.suffix.lower()
            ext_desc = self.extensions_data.get(ext, "Unknown Type")
            
            basic_info_table.add_row("Name", path.name)
            basic_info_table.add_row("Full Path", str(path.resolve()))
            basic_info_table.add_row("Type", "Directory" if is_dir else f"File ({ext_desc})")
            
            if is_dir:
                with console.status("[bold yellow]Calculating directory size...[/]"):
                    dir_size = sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())
                basic_info_table.add_row("Total Size", self.get_formatted_size(dir_size))
            else:
                basic_info_table.add_row("Size", self.get_formatted_size(file_stats.st_size))

            console.print(Panel(basic_info_table, title="[bold cyan]❯ Basic Info[/]", border_style="cyan"))

            # ... (The rest of the 'try' block for displaying panels remains unchanged) ...
            # --- Panel 2: Dates & Times ---
            dates_table = Table(box=None, show_header=False, expand=True)
            dates_table.add_column("Property", style="bold magenta", justify="right", width=20)
            dates_table.add_column("Value", style="green")
            
            dates_table.add_row("Last Modified", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stats.st_mtime)))
            dates_table.add_row("Last Accessed", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stats.st_atime)))
            dates_table.add_row("Created / Metadata Changed", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stats.st_ctime)))
            
            console.print(Panel(dates_table, title="[bold yellow]❯ Timestamps[/]", border_style="yellow"))
            
            # --- Panel 3: Permissions & Ownership ---
            perms_table = Table(box=None, show_header=False, expand=True)
            perms_table.add_column("Property", style="bold magenta", justify="right", width=20)
            perms_table.add_column("Value", style="green")
            
            perms = self.get_permissions(file_stats.st_mode)
            perms_table.add_row("Permissions (Octal)", oct(file_stats.st_mode)[-3:])
            perms_table.add_row("Permissions (Symbolic)", perms)
            
            try:
                owner = path.owner()
                group = path.group()
                perms_table.add_row("Owner", f"{owner} (UID: {file_stats.st_uid})")
                perms_table.add_row("Group", f"{group} (GID: {file_stats.st_gid})")
            except (KeyError, ImportError):
                perms_table.add_row("Owner UID", str(file_stats.st_uid))
                perms_table.add_row("Group GID", str(file_stats.st_gid))

            console.print(Panel(perms_table, title="[bold blue]❯ Permissions[/]", border_style="blue"))
            
            # --- Panel 4: Hashes (for files only) ---
            if not is_dir and file_stats.st_size > 0:
                with console.status("[bold yellow]Calculating file hashes...[/]"):
                    hashes = self.calculate_hashes(path)
                
                if hashes:
                    hashes_table = Table(box=None, show_header=False, expand=True)
                    hashes_table.add_column("Algorithm", style="bold magenta", justify="right", width=20)
                    hashes_table.add_column("Hash", style="green")
                    hashes_table.add_row("MD5", hashes['md5'])
                    hashes_table.add_row("SHA1", hashes['sha1'])
                    hashes_table.add_row("SHA256", hashes['sha256'])
                    console.print(Panel(hashes_table, title="[bold red]❯ File Hashes[/]", border_style="red"))

        except Exception as e:
            # --- CORE CHANGE: Use logger for unexpected errors ---
            env.log.error(f"An unexpected error occurred: {e}", exc_info=True)