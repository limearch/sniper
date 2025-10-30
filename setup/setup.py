# File: setup.py | Language: Python
# Description: Universal dependency installer for the SNIPER project. (pip update disabled)

import os
import sys
import json
import subprocess
import shutil
import importlib.util
from pathlib import Path
from typing import List, Dict, Any

# --------- import sniper env script ----------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
# import env script
from lib.sniper_env import env
# --- Colors for Output (Matching sniper tools) ---
from lib.sniper_env import Colors

# select a name to be on the logs
env.log.name = "setup"
# --- Configuration & Globals ---
dir_name = os.path.dirname(os.path.abspath(__file__)) 
PACKAGES_FILE = f"{dir_name}/packages.json"

# --- Mapping for pip packages with different import names ---
PIP_TO_IMPORT_MAP = {
    "beautifulsoup4": "bs4",
    "pyrebase4": "pyrebase",
    # Add other mappings here if needed, e.g., "Pillow": "PIL"
}


# --- State Management ---
SUCCESS_COUNT = 0
FAIL_COUNT = 0
TOTAL_OPS = 0

# --- Helper Functions ---

def print_header():
    print(f"{Colors.MAGENTA}╭───────────────────────────────────────────╮{Colors.RESET}")
    print(f"{Colors.MAGENTA}│   SNIPER: Universal Dependency Installer   │{Colors.RESET}")
    print(f"{Colors.MAGENTA}╰───────────────────────────────────────────╯{Colors.RESET}")

def print_section(title: str):
    print(f"\n{Colors.BLUE}--- {title} ---{Colors.RESET}")

def report_status(action: str, target: str, success: bool, output: str = ""):
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


def load_packages() -> Dict[str, Any]:
    try:
        with open(PACKAGES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        env.log.critical(f"The '{PACKAGES_FILE}' was not found. Cannot proceed.")
        sys.exit(1)
    except json.JSONDecodeError:
        env.log.error(f"The '{PACKAGES_FILE}' is not a valid JSON file. Please check its syntax.")
        sys.exit(1)

# --- Check Functions ---


def check_system_package(pkg: str) -> bool:
    """
    Checks if a system package is installed using the native package manager (dpkg).
    This is far more reliable than shutil.which for libraries and toolchains.
    """
    try:
        # Use dpkg to query the package status directly. This works reliably in Termux.
        # We redirect stdout and stderr to DEVNULL to keep the script output clean.
        result = subprocess.run(
            ['dpkg', '-s', pkg],
            check=False, # Important: Don't raise an exception on failure
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # A return code of 0 means the package is installed and configured.
        return result.returncode == 0
    except FileNotFoundError:
        # Fallback to the old method if 'dpkg' is somehow not found.
        return shutil.which(pkg) is not None
def check_pip_package(pkg: str) -> bool:
    """
    Checks if a Python package is installed and importable.
    Improved to handle different import names and edge cases.
    """
    try:
        import_name = PIP_TO_IMPORT_MAP.get(pkg, pkg.replace('-', '_'))

        # First: use importlib to check presence quickly
        if importlib.util.find_spec(import_name) is not None:
            return True

        # Second: subprocess isolation fallback
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
    command = install_cmd.split() + [pkg]
    print(f"  {Colors.CYAN}❯ Installing '{Colors.BOLD}{pkg}{Colors.RESET}{Colors.CYAN}'...{Colors.RESET}", end="", flush=True)
    success, output = run_command(command)
    report_status("Install system package", pkg, success, output)

def install_pip_package(pkg: str):
    command = [sys.executable, "-m", "pip", "install", "--upgrade", pkg]
    print(f"  {Colors.CYAN}❯ Installing '{Colors.BOLD}{pkg}{Colors.RESET}{Colors.CYAN}'...{Colors.RESET}", end="", flush=True)
    success, output = run_command(command)
    report_status("Install pip package", pkg, success, output)

# --- Main Logic ---

def run_check(packages: Dict, platform: str):
    print_section("Checking System Packages")
    if platform in packages.get("system", {}):
        sys_pkgs = packages["system"][platform]["packages"]
        for pkg in sys_pkgs:
            if 'dev' in pkg or 'essential' in pkg:
                print(f"  [{Colors.YELLOW}i{Colors.RESET}] {Colors.YELLOW}Info:{Colors.RESET} Skipping check for dev package '{pkg}'.")
                continue
            is_installed = check_system_package(pkg)
            report_status("Check system package", pkg, is_installed)
    else:
        env.log.warning(f"No system packages defined for platform '{platform}'. Skipping.")

    print_section("Checking Python Libraries (pip)")
    pip_pkgs = packages.get("python", [])
    for pkg in pip_pkgs:
        is_installed = check_pip_package(pkg)
        report_status("Check pip library", pkg, is_installed)

def run_install(packages: Dict, platform: str):
    """Runs the installation process, checking for existing packages first."""
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
                env.log.name = "setup"
                env.log.warning("Failed to update package lists. Continuing installation anyway...")

        for pkg in sys_pkgs:
            if check_system_package(pkg):
                print(f"  [{Colors.GREEN}✔{Colors.RESET}] {Colors.YELLOW}Exists:{Colors.RESET} System package '{pkg}' already installed.")
            else:
                install_system_package(pkg, install_cmd)
    else:
        env.log.warning(f"No system packages defined for platform '{platform}'. Skipping.")

    print_section("Installing Python Libraries (pip)")
    pip_pkgs = packages.get("python", [])
    
    # [تعديل] تم تعطيل التحديث التلقائي لـ pip
    # print(f"  {Colors.CYAN}❯ Upgrading pip...{Colors.RESET}", end="", flush=True)
    # success, output = run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    # report_status("Upgrade pip", "pip", success, output)

    for pkg in pip_pkgs:
        if check_pip_package(pkg):
            print(f"  [{Colors.GREEN}✔{Colors.RESET}] {Colors.YELLOW}Exists:{Colors.RESET} Python library '{pkg}' already installed.")
        else:
            install_pip_package(pkg)

def print_final_report():
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

    try:
        mode = "install"
        if len(sys.argv) > 1 and sys.argv[1].lower() == "check":
            mode = "check"

        platform = env.PLATFORM
        env.log.info(f"Detected System:{Colors.WHITE}({Colors.GREEN}{platform}{Colors.WHITE}){Colors.RESET}")
        env.log.info(f"Operation Mode: {Colors.BOLD}{Colors.WHITE}({Colors.GREEN}{mode}{Colors.WHITE}){Colors.RESET}")

        if platform == 'unknown':
            env.log.error("Could not determine your operating system. Aborting.")
            sys.exit(1)

        packages = load_packages()

        if mode == "install":
            run_install(packages, platform)
        else:
            run_check(packages, platform)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[WARN]{Colors.RESET} Operation interrupted by user (Ctrl+C).")
    finally:
        print_final_report()
        if FAIL_COUNT > 0:
            sys.exit(1)

if __name__ == "__main__":
    main()
