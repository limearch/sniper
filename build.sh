#!/bin/bash

# ==============================================================================
# SNIPER: Universal Build, Clean & Permissions Script
# ==============================================================================

# --- Configuration & Globals ---

# Get the absolute path to the directory containing this script (e.g., /path/to/sniper/bin)
PROJECT_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
# Go up one level to the project root (e.g., /path/to/sniper)
# PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

# --- List of all executables in the project ---
# Paths are relative to PROJECT_ROOT
EXECUTABLE_FILES=(
    "bin/activate"
    "bin/site-crafter"
    "bin/timer"
    "bin/combined"
    "bin/readme"
    "bin/lsmap"
    "bin/net-descover"
    "bin/lib-installer"
    "bin/listen"
    "bin/text-image"
    "bin/iplookup"
    "bin/scan"
    "bin/view-source"
    "tools/file-info/bin/file-info"
    "tools/shell-game/bin/shell-game"
    "tools/sniper-project-init/bin/sniper-init"
    "tools/social_dive/bin/social-dive"
    "tools/format/bin/format"
)

# Tools that need compilation via 'make'
TOOLS_TO_BUILD=(
    "tools/fastfind"
    "tools/compress"
    "tools/config"
    "tools/run"
    "tools/size"
)
# Add compiled executables to the main list
EXECUTABLE_FILES+=(
    "tools/fastfind/bin/fastfind"
    "tools/compress/bin/compress"
    "tools/config/bin/configer"
    "tools/run/bin/run"
    # "tools/size/bin/size"
)


# --- Colors for Output ---
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_BLUE='\033[0;36m'
C_MAGENTA='\033[0;35m'
C_CYAN='\033[0;36m'
C_GREY='\033[90m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

# --- State Management ---
SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL_OPS=0

# --- Helper Functions ---

function print_header() {
    echo -e "${C_MAGENTA}╭───────────────────────────────────────────╮${C_RESET}"
    echo -e "${C_MAGENTA}│   SNIPER: Build, Clean & Permissions Utility   │${C_RESET}"
    echo -e "${C_MAGENTA}╰───────────────────────────────────────────╯${C_RESET}"
}

# Reports the status of an operation
function report_status() {
    local action="$1"
    local target="$2"
    local exit_code="$3"
    local output="$4"

    TOTAL_OPS=$((TOTAL_OPS + 1))
    
    if [ "$exit_code" -eq 0 ]; then
        # Overwrite the "Processing..." line with the success status
        echo -e "\r  [${C_GREEN}✔${C_RESET}] ${C_GREEN}Success:${C_RESET} ${action} '${target}' completed.                                "
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "\r  [${C_RED}✘${C_RESET}] ${C_RED}Failure:${C_RESET} ${action} '${target}' failed."
        FAIL_COUNT=$((FAIL_COUNT + 1))
        if [[ -n "$output" ]]; then
            echo -e "${C_GREY}--- Error Output ---"
            echo -e "${output}" | sed 's/^/    /g' # Indent the output for readability
            echo -e "--- End Output ---${C_RESET}"
        fi
    fi
}


function run_make_command() {
    local action=$1
    local tool_rel_path=$2
    local make_target=$3
    
    local tool_name=$(basename "$tool_rel_path")
    local tool_abs_path="$PROJECT_ROOT/$tool_rel_path"

    echo -en "  ${C_CYAN}❯ ${action} '${C_BOLD}${tool_name}${C_RESET}${C_CYAN}'...${C_RESET}"

    if [ ! -d "$tool_abs_path" ] || [ ! -f "$tool_abs_path/Makefile" ]; then
        report_status "${action}" "${tool_name}" 1 "Makefile not found at ${tool_abs_path}"
        return
    
    fi
    local output
    output=$(make -C "$tool_abs_path" "$make_target" 2>&1)
    report_status "${action}" "${tool_name}" $? "$output"
}

function manage_permissions() {
    local mode=$1 # '+x' or '-x'
    local action_desc=""
    if [[ "$mode" == "+x" ]]; then
        action_desc="Setting executable"
    else
        action_desc="Removing executable"
    fi
    
    echo -e "\n${C_BLUE}--- ${action_desc} Permissions ---${C_RESET}"

    for file_rel_path in "${EXECUTABLE_FILES[@]}"; do
        local file_abs_path="$PROJECT_ROOT/$file_rel_path"
        local file_name=$(basename "$file_abs_path")
        
        echo -en "  ${C_CYAN}❯ Processing '${C_BOLD}${file_name}${C_RESET}${C_CYAN}'...${C_RESET}"
        
        if [ -f "$file_abs_path" ]; then
            chmod "$mode" "$file_abs_path"
            report_status "${action_desc}" "${file_name}" $? ""
        else
            # It's okay if a compiled file doesn't exist yet, especially during 'clean' or before 'build'
            if [[ "$mode" == "-x" ]]; then
                 report_status "${action_desc}" "${file_name}" 0 "" # It's not executable if it doesn't exist, so success.
            else
                 report_status "${action_desc}" "${file_name}" 1 "File not found."
            fi
        fi
    done
}


function rebuild_all() {
    echo -e "\n${C_BLUE}--- Starting Full Rebuild ---${C_RESET}"
    for tool_path in "${TOOLS_TO_BUILD[@]}"; do
        run_make_command "Building" "$tool_path" "all"
    done
    manage_permissions "+x"
}

function clean_all() {
    echo -e "\n${C_BLUE}--- Starting Full Clean ---${C_RESET}"
    manage_permissions "-x" # Remove permissions from all scripts and binaries
    for tool_path in "${TOOLS_TO_BUILD[@]}"; do
        run_make_command "Cleaning" "$tool_path" "clean"
    done
}

function print_final_report() {
    echo -e "\n${C_MAGENTA}╭──────────────────╮${C_RESET}"
    echo -e "${C_MAGENTA}│   Final Report   │${C_RESET}"
    echo -e "${C_MAGENTA}╰──────────────────╯${C_RESET}"
    echo -e "  Total Operations: ${C_BOLD}${TOTAL_OPS}${C_RESET}"
    echo -e "  ${C_GREEN}Successful: ${SUCCESS_COUNT}${C_RESET}"
    echo -e "  ${C_RED}Failed/Skipped: ${FAIL_COUNT}${C_RESET}"
    echo "--------------------"

    if [ $FAIL_COUNT -eq 0 ]; then
        echo -e "${C_GREEN}${C_BOLD}✅ All operations completed successfully!${C_RESET}"
    else
        echo -e "${C_RED}${C_BOLD}❌ Some operations failed. Please review the errors above.${C_RESET}"
    fi
}

function show_help() {
    print_header
    echo -e "\n  A script to build, clean, and manage permissions for all tools in the SNIPER project.\n"
    echo -e "  ${C_BOLD}USAGE:${C_RESET}"
    echo -e "    ${C_YELLOW}./build.sh${C_RESET} [command]\n"
    echo -e "  ${C_BOLD}COMMANDS:${C_RESET}"
    echo -e "    (no command)    Builds all C/C++ tools and sets executable permissions."
    echo -e "    ${C_GREEN}build${C_RESET}          Alias for the default build action."
    echo -e "    ${C_GREEN}clean${C_RESET}          Removes executable permissions and cleans all build artifacts."
    echo -e "    ${C_GREEN}help${C_RESET}           Shows this help message."
}

# --- Main Execution Logic ---

print_header

# Default action is 'build' if no argument is provided
ACTION="build"
if [[ $# -ge 1 ]]; then
    ACTION="$1"
fi

case "$ACTION" in
    build)
        rebuild_all
        ;;
    clean)
        clean_all
        ;;
    help)
        show_help
        exit 0
        ;;
    *)
        echo -e "\n${C_RED}Error: Unknown command '${ACTION}'.${C_RESET}"
        show_help
        exit 1
        ;;
esac

print_final_report

# Exit with a non-zero status if any operation failed
if [ $FAIL_COUNT -ne 0 ]; then
    exit 1
fi
