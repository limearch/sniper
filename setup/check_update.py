#!/usr/bin/env python3
# File: setup/check_update.py (v3.1 - Final, Correct Lock-File Implementation)

import sys
import subprocess
import time
from pathlib import Path

# --- Core SNIPER Environment Integration ---
try:
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(_PROJECT_ROOT))
    from lib.sniper_env import env, Colors
    env.log.name = "check-update"
except (ImportError, IndexError):
    class Colors:
        RESET = '\033[0m'; BOLD = '\033[1m'; RED = '\033[0;31m'
        GREEN = '\033[0;32m'; YELLOW = '\033[0;33m'; CYAN = '\033[0;36m'
    print(f"{Colors.RED}[CRITICAL ERROR]{Colors.RESET} Could not initialize SNIPER environment.", file=sys.stderr)
    sys.exit(1)

# --- Constants & Configuration ---
GITHUB_USER = "limearch"
GITHUB_REPO = "sniper"
CHANGELOG_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/CHANGELOG.md"

def run_git_command(command: list) -> str | None:
    """Runs a Git command and returns its output, or None on failure."""
    try:
        result = env.run_command(command, cwd=env.ROOT_DIR)
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

def get_latest_published_version(content: str) -> str:
    """Parses changelog content to find the latest PUBLISHED version number."""
    for line in content.splitlines():
        if line.startswith("## [") and "Unreleased" not in line:
            try:
                return line.split('[')[1].split(']')[0]
            except IndexError:
                continue
    return "Unknown"

def get_current_version_info() -> tuple[str, str]:
    """Gets the current version and date from the local CHANGELOG.md file."""
    local_changelog = env.ROOT_DIR / "CHANGELOG.md"
    if not local_changelog.is_file():
        return "Unknown", "Unknown"
    
    with open(local_changelog, 'r', encoding='utf-8') as f:
        content = f.read()
    
    version = get_latest_published_version(content)
    date_str = "Unknown"
    for line in content.splitlines():
        if f"## [{version}]" in line:
            try:
                date_str = line.split('] - ')[1].strip()
            except IndexError:
                break
            break
    return version, date_str

def fetch_remote_changelog() -> str | None:
    """Fetches the changelog content from GitHub."""
    try:
        import requests
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(CHANGELOG_URL, timeout=7, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception:
        result = env.run_command(['curl', '-sL', CHANGELOG_URL])
        return result.stdout if result.returncode == 0 and result.stdout else None

def check_updates_interactive():
    """Handles the 'sniper check-update' command (user-invoked)."""
    print(f"{Colors.CYAN}[i]{Colors.RESET} Checking for updates...")
    
    if run_git_command(["git", "fetch", "origin"]) is None:
        print(f"{Colors.RED}[✘]{Colors.RESET} Network Error: Could not connect to GitHub.")
        return

    local_hash = run_git_command(["git", "rev-parse", "HEAD"])
    remote_hash = run_git_command(["git", "rev-parse", "origin/main"])
    current_version, last_update_date = get_current_version_info()

    if not local_hash or not remote_hash:
        print(f"{Colors.RED}[✘]{Colors.RESET} Git Error: Could not determine local or remote version.")
        return

    print("-" * 45)
    print(f"{Colors.BOLD}SNIPER Update Status{Colors.RESET}")
    print(f"  {Colors.CYAN}❯{Colors.RESET} Your Version:    {Colors.BOLD}{current_version}{Colors.RESET} ({last_update_date})")

    if local_hash == remote_hash:
        print(f"  {Colors.GREEN}❯{Colors.RESET} Status:          {Colors.BOLD}{Colors.GREEN}Up to Date{Colors.RESET}")
    else:
        latest_version_str = "New" # Default
        remote_changelog = fetch_remote_changelog()
        
        if remote_changelog:
            latest_published_version = get_latest_published_version(remote_changelog)
            try:
                if (latest_published_version != "Unknown" and current_version != "Unknown" and
                    tuple(map(int, latest_published_version.split('.'))) > tuple(map(int, current_version.split('.')))):
                    latest_version_str = latest_published_version
                else:
                    latest_version_str = "Next (Unreleased)"
            except (ValueError, TypeError):
                 latest_version_str = "Next (Unreleased)"
        else:
            latest_version_str = f"[{Colors.RED}Fetch Failed{Colors.RESET}]"
        
        print(f"  {Colors.YELLOW}❯{Colors.RESET} Latest Version:  {Colors.BOLD}{latest_version_str}{Colors.RESET}")
        print(f"  {Colors.GREEN}❯{Colors.RESET} Action:          Run '{Colors.BOLD}sniper update{Colors.RESET}' to install.")
    print("-" * 45)

def check_updates_silent():
    """
    Handles the automatic, background update check using the CORRECT lock file mechanism.
    """
    config = env.config.get('update', {})
    check_interval = config.get('check_interval_seconds', 86400) # 24 hours
    
    # --- Correct File Names ---
    update_lock_file = env.CONFIG_DIR / ".update_available"
    last_check_file = env.CONFIG_DIR / ".last_update_check"

    # --- Logic 1: If lock file exists, notify and exit immediately. ---
    if update_lock_file.exists():
        latest_version = update_lock_file.read_text().strip()
        print(f"{Colors.YELLOW}[i]{Colors.RESET} Update available ({Colors.BOLD}{latest_version}{Colors.RESET}). Run '{Colors.GREEN}sniper update{Colors.RESET}'.", file=sys.stderr)
        return

    # --- Logic 2: If lock file does NOT exist, check if it's time for a network check. ---
    if last_check_file.exists() and (time.time() - last_check_file.stat().st_mtime) < check_interval:
        return # Not time yet, exit silently.

    last_check_file.touch() # Update the check timestamp before making a network call.

    # --- Logic 3: Perform the actual network check. ---
    if run_git_command(["git", "fetch", "origin"]) is None:
        return # Silently fail on network error.
        
    local_hash = run_git_command(["git", "rev-parse", "HEAD"])
    remote_hash = run_git_command(["git", "rev-parse", "origin/main"])

    if local_hash and remote_hash and local_hash != remote_hash:
        # An update (versioned or unreleased) is found. Determine what to display.
        latest_version_str = "New" # Default value
        remote_changelog = fetch_remote_changelog()
        if remote_changelog:
            current_version, _ = get_current_version_info()
            latest_published_version = get_latest_published_version(remote_changelog)
            try:
                # Logic to decide if it's a new version or unreleased changes
                if (latest_published_version != "Unknown" and current_version != "Unknown" and
                    tuple(map(int, latest_published_version.split('.'))) > tuple(map(int, current_version.split('.')))):
                    latest_version_str = latest_published_version
                else:
                    latest_version_str = "Next (Unreleased)"
            except (ValueError, TypeError):
                latest_version_str = "Next (Unreleased)"
        
        # --- Logic 4: Create the lock file with the determined version string. ---
        update_lock_file.write_text(latest_version_str)
        # Recurse to immediately print the notification message.
        check_updates_silent()

def main():
    """Main entry point, determines which mode to run."""
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "check-update":
            check_updates_interactive()
        else:
            check_updates_silent()
    except Exception as e:
        env.log.error(f"Update check failed unexpectedly: {e}", exc_info=False)

if __name__ == "__main__":
    main()
