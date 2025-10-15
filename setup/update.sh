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

    # Step 1: Change to the project root directory
    cd "$PROJECT_ROOT" || {
        echo -e "${C_RED}[✘] Error:${C_RESET} Could not change to project directory: ${PROJECT_ROOT}"
        return 1
    }

    # --- Step 2: High-Risk User Confirmation ---
    echo
    echo -e "${C_YELLOW}${C_BOLD}⚠️ HIGH RISK ACTION ⚠️${C_RESET}"
    echo -e "This process will permanently overwrite your local files with the latest version from GitHub."
    echo -e "${C_RED}Any changes you have made since installation will be lost forever.${C_RESET}"
    echo
    read -p "  ❯ Do you understand the risk and wish to continue? (yes/no): " -r
    if [[ ! "$REPLY" =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "\n${C_RED}Update aborted by user.${C_RESET}"
        return 1
    fi
    
    echo
    read -p "  ❯ ARE YOU ABSOLUTELY SURE? This cannot be undone. (yes/no): " -r
    if [[ ! "$REPLY" =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "\n${C_RED}Update aborted by user.${C_RESET}"
        return 1
    fi

    # --- Step 3: Optional Backup ---
    echo
    echo -e "  ${C_YELLOW}Hint: A backup is highly recommended if you have made any changes.${C_RESET}"
    read -p "  ❯ Would you like to create a backup of the current state? (yes/no): " -r
    if [[ "$REPLY" =~ ^[Yy][Ee][Ss]$ ]]; then
        print_step "Creating backup"
        
        # Define backup path: ~/backup/sniper-YYYY-MM-DD_HH-MM-SS
        local backup_dir="$HOME/backup"
        local timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
        local current_version=$(awk -F '[][]' '/^## \[/ && !/Unreleased/ {print $2; exit}' CHANGELOG.md)
        local backup_name="sniper-${current_version:-unknown}-${timestamp}"
        local backup_path="$backup_dir/$backup_name"

        mkdir -p "$backup_dir"
        
        # Using cp instead of tar for simplicity and to avoid tar errors
        cp -r "$PROJECT_ROOT" "$backup_path"
        local backup_status=$?

        print_status $backup_status
        if [ $backup_status -eq 0 ]; then
            echo -e "    ${C_GREEN}Backup saved to: ${backup_path}${C_RESET}"
        else
            echo -e "${C_RED}[✘] Error:${C_RESET} Backup failed. Aborting update to be safe."
            return 1
        fi
    fi

    # --- Step 4: Force Update using Git Reset ---
    print_stage "Fetching and Applying Updates"

    print_step "Fetching latest version data from GitHub"
    git fetch origin main >/dev/null 2>&1
    print_status $?

    print_step "Forcibly resetting local files to match remote"
    # This command discards all local changes and makes the local branch identical to the remote one.
    git_output=$(git reset --hard origin/main 2>&1)
    git_reset_status=$?
    print_status $git_reset_status

    if [ $git_reset_status -ne 0 ]; then
        echo -e "${C_RED}[✘] Error:${C_RESET} 'git reset --hard' failed."
        echo -e "    ${C_YELLOW}Git Output:${C_RESET}\n$git_output"
        return 1
    fi

    # --- Step 5: Rebuild, Update Dependencies, and Cleanup (Same as before) ---
    print_stage "Rebuilding Project & Updating Environment"

    print_step "Compiling C/C++ tools and setting permissions"
    ./setup/build build > /dev/null 2>&1
    build_status=$?
    print_status $build_status
    if [ $build_status -ne 0 ]; then
        echo -e "${C_YELLOW}[!] Warning:${C_RESET} Build script reported errors."
    fi

    print_step "Checking for new dependencies"
    python3 setup/setup.py > /dev/null 2>&1
    setup_status=$?
    print_status $setup_status
    if [ $setup_status -ne 0 ]; then
        echo -e "${C_YELLOW}[!] Warning:${C_RESET} Dependency installation reported errors."
    fi

    print_step "Resetting update checker"
    rm -f "$HOME/.cache/sniper/.update_available"
    print_status 0

    echo -e "\n${C_GREEN}✅ ${C_BOLD}SNIPER has been updated successfully!${C_RESET}"
    echo -e "--- ${C_BOLD}Recent Changes${C_RESET} ---"
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
