#!/bin/bash
# File: setup/update.sh (v2.0 - Final Version)
# Description: Performs the actual update process for the SNIPER toolkit.
# This script is called by the main 'sniper' command.

# --- Configuration & Globals ---
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

# --- Colors for Output ---
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_BLUE='\033[0;36m'
C_CYAN='\033[0;36m'
C_RESET='\033[0m'
C_BOLD='\033[1m'

# --- Helper Functions ---

print_stage() {
    echo -e "\n${C_BLUE}--- $1 ---${C_RESET}"
}

print_step() {
    echo -en "  ${C_CYAN}❯${C_RESET} $1..."
}

print_status() {
    if [ "$1" -eq 0 ]; then
        echo -e "${C_GREEN}Done.${C_RESET}"
    else
        echo -e "${C_RED}Failed.${C_RESET}"
    fi
}

# --- Main Update Function ---

perform_update() {
    print_stage "Starting SNIPER Update"
    
    # Step 1: Verify we are in the project root
    cd "$PROJECT_ROOT" || {
        echo -e "${C_RED}[✘] Error:${C_RESET} Could not change to project directory: ${PROJECT_ROOT}"
        return 1
    }

    # Step 2: Check for local modifications (Safety First)
    print_step "Checking for local changes"
    if [[ -n $(git status --porcelain) ]]; then
        print_status 1 # Mark step as failed
        echo -e "${C_RED}[✘] Aborting update:${C_RESET} You have uncommitted local changes."
        echo -e "    Please commit or stash your changes before updating."
        echo -e "    ${C_YELLOW}Hint:${C_RESET} Run 'git status' to see the modified files."
        return 1
    fi
    print_status 0

    # Step 3: Pull the latest updates from the remote repository
    print_step "Pulling latest updates from GitHub"
    git_output=$(git pull origin main 2>&1)
    git_pull_status=$?
    print_status $git_pull_status
    if [ $git_pull_status -ne 0 ]; then
        echo -e "${C_RED}[✘] Error:${C_RESET} 'git pull' failed. Please resolve any issues and try again."
        echo -e "    ${C_YELLOW}Git Output:${C_RESET}\n$git_output"
        return 1
    fi

    # Step 4: Rebuild project tools using the dynamic build script
    print_stage "Rebuilding Project & Updating Environment"
    
    print_step "Compiling C/C++ tools and setting permissions"
    ./setup/build build > /dev/null 2>&1
    build_status=$?
    print_status $build_status
    if [ $build_status -ne 0 ]; then
        echo -e "${C_YELLOW}[!] Warning:${C_RESET} The build script reported errors. Some tools may not work correctly."
        echo -e "    Run './setup/build' manually to see the full output."
    fi

    # Step 5: Update Python/System dependencies
    print_step "Checking for new dependencies"
    python3 setup/setup.py > /dev/null 2>&1
    setup_status=$?
    print_status $setup_status
    if [ $setup_status -ne 0 ]; then
        echo -e "${C_YELLOW}[!] Warning:${C_RESET} Dependency installation reported errors."
        echo -e "    Run 'python3 setup/setup.py' manually to see the full output."
    fi

    # Step 6: Reset the update checker by removing the lock file
    print_step "Resetting update checker"
    rm -f "$PROJECT_ROOT/config/.update_available"
    print_status 0

    # Step 7: Display the most recent changes to the user
    echo -e "\n${C_GREEN}✅ ${C_BOLD}SNIPER has been updated successfully!${C_RESET}"
    echo -e "--- ${C_BOLD}Recent Changes${C_RESET} ---"
    # awk command to print content between the first and second '## [' lines
    awk '/^## \[/{c++; if(c==2) exit} c>=1' CHANGELOG.md | tail -n +2 | sed 's/^/  /g'
}

# --- Main Execution Logic ---

# This script expects to be called with a specific command.
if [[ "$1" == "run" ]]; then
    perform_update
else
    echo -e "${C_RED}Error:${C_RESET} This script is an internal part of the SNIPER toolkit."
    echo "Please use the '${C_YELLOW}sniper update${C_RESET}' command to run it."
    exit 1
fi
