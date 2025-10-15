# File: tools/social_dive/social_dive_tool/core.py (REFACTORED)

import sys
import json
import requests
import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- START: Core Integration ---
# This module is now imported by the entrypoint, which has already set up the path.
# We can directly import the environment.
try:
    from lib.sniper_env import env
except ImportError:
    # Fallback for isolated testing
    print("\033[91m[CRITICAL ERROR]\033[0m Could not import SNIPER environment.", file=sys.stderr)
    class DummyLog:
        def error(self, msg): print(f"[ERROR] {msg}", file=sys.stderr)
        def warning(self, msg): print(f"[WARN] {msg}", file=sys.stderr)
        def info(self, msg): print(f"[INFO] {msg}", file=sys.stderr)
    class DummyEnv:
        log = DummyLog()
    env = DummyEnv()
# --- END: Core Integration ---

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
except ImportError:
    env.log.critical("The 'rich' library is required. Please run: pip install rich")
    sys.exit(1)

console = Console()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

def load_data(category_filter=None):
    """Loads and filters site data from data.json."""
    try:
        data_file_path = Path(__file__).parent / "data.json"
        with open(data_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if category_filter:
            category_lower = category_filter.lower()
            filtered_data = {
                name: info for name, info in data.items()
                if info.get("category", "").lower() == category_lower
            }
            if not filtered_data:
                # --- CORE CHANGE: Use logger for warnings ---
                env.log.warning(f"No sites found for category '{category_filter}'. Exiting.")
                sys.exit(0) # Exit gracefully
            return filtered_data
        return data
    except FileNotFoundError:
        # --- CORE CHANGE: Use logger for critical errors ---
        env.log.critical("data.json not found! The tool cannot function without it.")
        sys.exit(1)
    except json.JSONDecodeError:
        env.log.critical("Could not decode data.json. Check for syntax errors.")
        sys.exit(1)

def check_username(site_name, site_info, username, timeout, proxy):
    """Checks for a username on a single site."""
    # This function's logic remains unchanged. It is performance-critical and
    # should not have I/O (like logging) inside it.
    url = site_info['url'].replace('%s', username)
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, proxies=proxies, allow_redirects=True)
        check_type = site_info.get("type", "statusCode")

        if check_type == "statusCode" and r.status_code == 200:
            return site_name, url
        elif check_type == "stringCheck" and site_info.get("error_string") not in r.text:
            return site_name, url
        elif check_type == "errorCode" and r.status_code != site_info.get("error_code"):
            return site_name, url
            
    except requests.exceptions.RequestException:
        pass # Silently ignore connection/timeout errors.
    except Exception:
        pass # Silently ignore other unexpected errors.
        
    return None, None

def export_results(filename, found_accounts):
    """Exports found accounts to the specified file format."""
    sorted_accounts = sorted(found_accounts, key=lambda x: x['name'])
    
    if not sorted_accounts:
        env.log.warning("No accounts found to export.")
        return

    env.log.info(f"Exporting {len(sorted_accounts)} found accounts to '{filename}'...")
    
    try:
        if filename.endswith('.txt'):
            with open(filename, 'w', encoding='utf-8') as f:
                for acc in sorted_accounts: f.write(f"{acc['name']}: {acc['url']}\n")
        elif filename.endswith('.csv'):
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Website', 'URL'])
                for acc in sorted_accounts: writer.writerow([acc['name'], acc['url']])
        elif filename.endswith('.json'):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(sorted_accounts, f, indent=4)
        else:
            env.log.warning(f"Unsupported format for '{filename}'. Use .txt, .csv, or .json.")
            return
        
        # Use console.print for green success message to stand out.
        console.print(f"[[bold green]+[/]] Results successfully exported.")
    except Exception as e:
        env.log.error(f"Failed to export results: {e}")

def run_scan(args):
    """Main execution flow: concurrent scanning and result display."""
    env.log.info(f"Searching for username: [bold]{args.username}[/]")
    sites_data = load_data(args.category)
    total_sites = len(sites_data)
    found_accounts = []

    # The Rich progress bar setup remains unchanged as it's a core UI element.
    progress = Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "({task.completed}/{task.total})",
        TextColumn("[bold green]Found: {task.fields[found_count]}[/]"),
        console=console
    )

    with progress:
        task = progress.add_task("Scanning...", total=total_sites, found_count=0)
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {
                executor.submit(check_username, name, info, args.username, args.timeout, args.proxy): name
                for name, info in sites_data.items()
            }
            
            for future in as_completed(futures):
                site_name, url = future.result()
                if site_name:
                    found_accounts.append({'name': site_name, 'url': url})
                    # We keep console.print here for the immediate visual feedback above the progress bar.
                    console.print(f"[[bold green]+[/]] [bold green]{site_name}:[/] {url}")
                
                progress.update(task, advance=1, found_count=len(found_accounts))
    
    console.rule(f"[bold green]Scan Complete[/]", style="green")
    console.print(f"Found [bold cyan]{len(found_accounts)}[/] account(s) across [bold cyan]{total_sites}[/] websites.")
    if args.output:
        export_results(args.output, found_accounts)
