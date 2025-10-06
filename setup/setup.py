# File: setup.py | Language: Python
# Description: Universal dependency installer for the SNIPER project. (Corrected Version 2)

import os
import sys
import json
import subprocess
import shutil
from typing import List, Dict, Any

# --- Configuration & Globals ---

PACKAGES_FILE = "packages.json"

# --- Mapping for pip packages with different import names ---
PIP_TO_IMPORT_MAP = {
    "beautifulsoup4": "bs4",
    "pyrebase4": "pyrebase",
    # Add other mappings here if needed, e.g., "Pillow": "PIL"
}

# --- Colors for Output (Matching sniper tools) ---
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    GREY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# --- State Management ---
SUCCESS_COUNT = 0
FAIL_COUNT = 0
TOTAL_OPS = 0

# --- Helper Functions ---

def print_info(message: str):
    """Prints an informational message."""
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {message}")

def print_error(message: str):
    """Prints an error message to stderr."""
    print(f"{Colors.RED}[ERROR]{Colors.RESET} {message}", file=sys.stderr)

def print_warn(message: str):
    """Prints a warning message."""
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {message}")

def print_header():
    """Prints the main header in SNIPER style."""
    print(f"{Colors.MAGENTA}╭───────────────────────────────────────────╮{Colors.RESET}")
    print(f"{Colors.MAGENTA}│   SNIPER: Universal Dependency Installer   │{Colors.RESET}")
    print(f"{Colors.MAGENTA}╰───────────────────────────────────────────╯{Colors.RESET}")

def print_section(title: str):
    """Prints a section header."""
    print(f"\n{Colors.BLUE}--- {title} ---{Colors.RESET}")

def report_status(action: str, target: str, success: bool, output: str = ""):
    """Reports the status of an operation and updates counters."""
    global TOTAL_OPS, SUCCESS_COUNT, FAIL_COUNT
    TOTAL_OPS += 1
    
    if success:
        SUCCESS_COUNT += 1
        print(f"\r  [{Colors.GREEN}✔{Colors.RESET}] {Colors.GREEN}Success:{Colors.RESET} {action} '{target}' completed.                                ")
    else:
        FAIL_COUNT += 1
        print(f"\r  [{Colors.RED}✘{Colors.RESET}] {Colors.RED}Failure:{Colors.RESET} {action} '{target}' failed.")
        if output:
            print(f"{Colors.GREY}--- Error Output ---")
            for line in output.strip().split('\n'):
                print(f"    {line}")
            print(f"--- End Output ---{Colors.RESET}")

def get_system_platform() -> str:
    """Determines the operating system (termux, debian, etc.)."""
    if 'com.termux' in os.environ.get('PREFIX', ''):
        return 'termux'
    if sys.platform.startswith('linux'):
        if os.path.exists('/etc/debian_version'):
            return 'debian'
    return 'unknown'

def load_packages() -> Dict[str, Any]:
    """Loads package definitions from packages.json."""
    try:
        with open(PACKAGES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print_error(f"The '{PACKAGES_FILE}' was not found. Cannot proceed.")
        sys.exit(1)
    except json.JSONDecodeError:
        print_error(f"The '{PACKAGES_FILE}' is not a valid JSON file. Please check its syntax.")
        sys.exit(1)

# --- Check Functions ---

def check_system_package(pkg: str) -> bool:
    """Checks if a system package (command) is available in PATH."""
    return shutil.which(pkg) is not None

def check_pip_package(pkg: str) -> bool:
    """
    Checks if a Python package is installed and importable.
    This is the corrected version that handles different import names.
    """
    try:
        # Use the map first, otherwise fall back to the default conversion.
        import_name = PIP_TO_IMPORT_MAP.get(pkg, pkg.replace('-', '_'))
        
        # Run a subprocess to isolate the import check.
        # Hide output unless there's an error for cleaner reporting.
        result = subprocess.run(
            [sys.executable, "-c", f"import {import_name}"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

# --- Install Functions ---

def run_command(command: List[str]) -> (bool, str):
    """Runs a command and returns its status and output."""
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=False)
        if process.returncode == 0:
            return True, process.stdout
        else:
            return False, process.stderr if process.stderr else process.stdout
    except FileNotFoundError:
        return False, f"Command not found: {command[0]}"
    except Exception as e:
        return False, str(e)

def install_system_package(pkg: str, install_cmd: str):
    """Installs a single system package."""
    command = install_cmd.split() + [pkg]
    print(f"  {Colors.CYAN}❯ Installing '{Colors.BOLD}{pkg}{Colors.RESET}{Colors.CYAN}'...{Colors.RESET}", end="", flush=True)
    success, output = run_command(command)
    report_status("Install system package", pkg, success, output)

def install_pip_package(pkg: str):
    """Installs a single Python package using pip."""
    command = [sys.executable, "-m", "pip", "install", "--upgrade", pkg]
    print(f"  {Colors.CYAN}❯ Installing '{Colors.BOLD}{pkg}{Colors.RESET}{Colors.CYAN}'...{Colors.RESET}", end="", flush=True)
    success, output = run_command(command)
    report_status("Install pip package", pkg, success, output)

# --- Main Logic ---

def run_check(packages: Dict, platform: str):
    """Runs the dependency check mode."""
    print_section("Checking System Packages")
    if platform in packages.get("system", {}):
        sys_pkgs = packages["system"][platform]["packages"]
        for pkg in sys_pkgs:
            # For dev packages, we can't easily check, so we assume a check is a 'skip'
            if 'dev' in pkg or 'essential' in pkg:
                print(f"  [{Colors.YELLOW}i{Colors.RESET}] {Colors.YELLOW}Info:{Colors.RESET} Skipping check for dev package '{pkg}'.")
                continue
            is_installed = check_system_package(pkg)
            report_status("Check system package", pkg, is_installed)
    else:
        print_warn(f"No system packages defined for platform '{platform}'. Skipping.")

    print_section("Checking Python Libraries (pip)")
    pip_pkgs = packages.get("python", [])
    for pkg in pip_pkgs:
        is_installed = check_pip_package(pkg)
        report_status("Check pip library", pkg, is_installed)

def run_install(packages: Dict, platform: str):
    """Runs the installation process."""
    print_section("Installing System Packages")
    if platform in packages.get("system", {}):
        platform_config = packages["system"][platform]
        update_cmd = platform_config.get("update_cmd")
        install_cmd = platform_config.get("install_cmd")
        sys_pkgs = platform_config.get("packages", [])

        if update_cmd:
            print(f"  {Colors.CYAN}❯ Updating package lists...{Colors.RESET}", end="", flush=True)
            success, output = run_command(update_cmd.split())
            report_status("Update package list", platform, success, output)
            if not success:
                print_warn("Failed to update package lists. Continuing installation anyway...")
        
        for pkg in sys_pkgs:
            install_system_package(pkg, install_cmd)
    else:
        print_warn(f"No system packages defined for platform '{platform}'. Skipping.")

    print_section("Installing Python Libraries (pip)")
    pip_pkgs = packages.get("python", [])
    print(f"  {Colors.CYAN}❯ Upgrading pip...{Colors.RESET}", end="", flush=True)
    success, output = run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    report_status("Upgrade pip", "pip", success, output)

    for pkg in pip_pkgs:
        install_pip_package(pkg)
        
def print_final_report():
    """Prints a summary of all operations."""
    print(f"\n{Colors.MAGENTA}╭──────────────────╮{Colors.RESET}")
    print(f"{Colors.MAGENTA}│   Final Report   │{Colors.RESET}")
    print(f"{Colors.MAGENTA}╰──────────────────╯{Colors.RESET}")
    print(f"  Total Operations: {Colors.BOLD}{TOTAL_OPS}{Colors.RESET}")
    print(f"  {Colors.GREEN}Successful: {SUCCESS_COUNT}{Colors.RESET}")
    print(f"  {Colors.RED}Failed/Missing: {FAIL_COUNT}{Colors.RESET}")
    print("--------------------")

    if FAIL_COUNT == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ All operations completed successfully!{Colors.RESET}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some operations failed. Please review the errors above.{Colors.RESET}")

def main():
    """Main entry point for the script."""
    print_header()
    
    mode = "install"
    if len(sys.argv) > 1 and sys.argv[1].lower() == "check":
        mode = "check"

    platform = get_system_platform()
    print_info(f"Detected System: {Colors.BOLD}{platform}{Colors.RESET}")
    print_info(f"Operation Mode: {Colors.BOLD}{mode}{Colors.RESET}")

    if platform == 'unknown':
        print_error("Could not determine your operating system. Aborting.")
        sys.exit(1)

    packages = load_packages()

    if mode == "install":
        run_install(packages, platform)
    else: # mode == "check"
        run_check(packages, platform)

    print_final_report()
    
    if FAIL_COUNT > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
