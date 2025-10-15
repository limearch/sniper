#!/bin/bash

# ==============================================================================
# SNIPER: format - Automated Test Suite (Final Version)
# ==============================================================================

# --- Configuration & Globals ---
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
EXECUTABLE_DIR="$PROJECT_ROOT/bin"
EXECUTABLE_NAME="format"
export PATH="$EXECUTABLE_DIR:$PATH"
TEST_DIR="format_test_dir"

# --- Colors for Output ---
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_BLUE='\033[0;34m'
C_MAGENTA='\033[0;35m'
C_CYAN='\033[0;36m'
C_GREY='\033[90m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

# --- State Management ---
TEST_RESULTS=()
TEST_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

# --- Cleanup Trap ---
trap "echo -e '\n${C_YELLOW}Cleaning up test environment...${C_RESET}'; rm -rf '$TEST_DIR'" EXIT

# --- Helper Functions ---

function print_box_title() {
    local title="   $1   "
    echo -e "${C_MAGENTA}╭───────────────────────────╮${C_RESET}"
    echo -e "${C_MAGENTA}│$title│${C_RESET}"
    echo -e "${C_MAGENTA}╰───────────────────────────╯${C_RESET}"
}

function print_stage() {
  echo -e "\n${C_BLUE}--- $1 ---${C_RESET}"
}

function run_test() {
    local description="$1"
    local command_str="$2"
    local validation_type="$3"
    local expected="$4"

    TEST_COUNT=$((TEST_COUNT + 1))
    echo -e "★ ${C_BOLD}${description}${C_RESET}"
    echo -e "→ ${C_GREY}Command: ${command_str}${C_RESET}"

    local output
    local exit_code
    
    output=$(eval "$command_str" 2>&1)
    exit_code=$?
    
    local success=0
    local reason=""

    case "$validation_type" in
        contains)
            if echo "$output" | grep -q -- "$expected"; then
                success=1
            else
                reason="Output was expected to contain '${expected}'."
            fi
            ;;
        not_contains)
            if ! echo "$output" | grep -q -- "$expected"; then
                success=1
            else
                reason="Output was NOT expected to contain '${expected}'."
            fi
            ;;
        exit_code)
             if [ "$exit_code" -eq "$expected" ]; then
                success=1
            else
                reason="Expected exit code '${expected}', but got '${exit_code}'."
            fi
            ;;
    esac

    if [ $success -eq 1 ]; then
        echo -e "[${C_GREEN}✔${C_RESET}] ${C_GREEN}Success${C_RESET}"
        PASS_COUNT=$((PASS_COUNT + 1))
        TEST_RESULTS+=("[${C_GREEN}✔${C_RESET}] ${description}")
    else
        echo -e "[${C_RED}✘${C_RESET}] ${C_RED}Failure${C_RESET}: ${reason}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        TEST_RESULTS+=("[${C_RED}✘${C_RESET}] ${description}")
    fi
    echo -e "${C_GREY}Output:\n${output}${C_RESET}"
    echo "------------------------------------------------------------"
}

function skip_test_if_missing() {
    local command_name="$1"
    local description="$2"
    if ! command -v "$command_name" &> /dev/null; then
        TEST_COUNT=$((TEST_COUNT + 1))
        SKIP_COUNT=$((SKIP_COUNT + 1))
        echo -e "★ ${C_BOLD}${description}${C_RESET}"
        echo -e "[${C_YELLOW}⊝${C_RESET}] ${C_YELLOW}Skipped${C_RESET}: Command '${command_name}' not found."
        TEST_RESULTS+=("[${C_YELLOW}⊝${C_RESET}] ${description}")
        echo "------------------------------------------------------------"
        return 1
    fi
    return 0
}


# --- Test Environment Setup ---
function setup_test_environment() {
  print_box_title "SNIPER: format - Test Suite"
  echo -e "${C_YELLOW}Setting up test environment in './${TEST_DIR}'...${C_RESET}"
  rm -rf "$TEST_DIR"
  mkdir -p "$TEST_DIR/subdir"
  
  echo "def my_func():\n  x=1+2\n  return x" > "$TEST_DIR/bad.py"
  echo '{"name":"sniper","version":"1.0"}' > "$TEST_DIR/data.json"
  echo -e "if [ -f file ]; then\necho 'file exists'\nfi" > "$TEST_DIR/script.sh"
  echo "def another_func():\n  pass" > "$TEST_DIR/subdir/another.py"

  echo -e "${C_YELLOW}Setup complete.${C_RESET}\n"
}

# --- Main Execution ---
function main() {
  if ! command -v "$EXECUTABLE_NAME" &> /dev/null; then
    echo -e "${C_RED}FATAL: Executable '$EXECUTABLE_NAME' not found in PATH ($EXECUTABLE_DIR).${C_RESET}"
    exit 1
  fi
  
  setup_test_environment

  print_stage "Core Functionality Tests"
  run_test "Format a single Python file" "$EXECUTABLE_NAME $TEST_DIR/bad.py && cat $TEST_DIR/bad.py" "contains" "    x = 1 + 2"
  run_test "Format a single JSON file" "$EXECUTABLE_NAME $TEST_DIR/data.json && cat $TEST_DIR/data.json" "contains" '    "name": "sniper"'
  
  if skip_test_if_missing "shfmt" "Format a Shell script"; then
    run_test "Format a Shell script" "$EXECUTABLE_NAME $TEST_DIR/script.sh && cat $TEST_DIR/script.sh" "contains" "	echo 'file exists'"
  fi

  print_stage "Feature Tests"
  echo "def my_func():\n  x=1+2\n  return x" > "$TEST_DIR/bad.py"
  run_test "Create a backup file" "$EXECUTABLE_NAME $TEST_DIR/bad.py -b && ls $TEST_DIR/bad.py.bak" "contains" "$TEST_DIR/bad.py.bak"
  
  echo "def my_func():\n  x=1+2\n  return x" > "$TEST_DIR/bad.py"
  run_test "Filter to format only .json" "$EXECUTABLE_NAME $TEST_DIR -f .json -v && cat $TEST_DIR/bad.py" "not_contains" "    x = 1 + 2"

  print_stage "Check Mode Tests"
  echo "def my_func():\n  x=1+2\n  return x" > "$TEST_DIR/bad.py"
  run_test "Check mode identifies unformatted files" "$EXECUTABLE_NAME $TEST_DIR/bad.py --check -v" "contains" "'$TEST_DIR/bad.py' needs formatting"
  run_test "Check mode exits with non-zero on failure" "$EXECUTABLE_NAME $TEST_DIR/bad.py --check" "exit_code" 1
  
  $EXECUTABLE_NAME $TEST_DIR/bad.py > /dev/null 2>&1
  run_test "Check mode exits with zero on success" "$EXECUTABLE_NAME $TEST_DIR/bad.py --check" "exit_code" 0
  
  print_stage "Recursive Directory Test"
  echo "def another_func():\n  pass" > "$TEST_DIR/subdir/another.py"
  run_test "Recursively format entire directory" "$EXECUTABLE_NAME $TEST_DIR -v" "contains" "Formatted '$TEST_DIR/subdir/another.py'"

  # --- Final Report ---
  print_box_title "Final Test Report"
  for i in "${!TEST_RESULTS[@]}"; do
    echo -e " $(($i + 1)). ${TEST_RESULTS[$i]}"
  done
  echo ""
  echo -e "★ Passed: ${C_GREEN}${PASS_COUNT}${C_RESET}   ★ Failed: ${C_RED}${FAIL_COUNT}${C_RESET}   ★ Skipped: ${C_YELLOW}${SKIP_COUNT}${C_RESET}   Total: ${C_BOLD}${TEST_COUNT}${C_RESET}"

  if [ $FAIL_COUNT -ne 0 ]; then
    exit 1
  fi
}

main
