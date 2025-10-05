#!/bin/bash

# ==============================================================================
# SNIPER: fastfind - Automated Test Suite v2.0
# ==============================================================================

# --- Configuration & Globals ---
EXECUTABLE="../tools/fastfind/bin/fastfind"
TEST_DIR="fastfind_test_dir"
CURRENT_USER=$(whoami)

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

# --- Cleanup Trap ---
trap "echo -e '\n${C_YELLOW}Cleaning up test environment...${C_RESET}'; rm -rf '$TEST_DIR' result.txt" EXIT

# --- Helper Functions ---

function print_box_title() {
    local title="   $1   "
    local len=${#title}
    local line="╭"
    for (( i=0; i<len; i++ )); do line+="─"; done
    line+="╮"
    echo -e "${C_MAGENTA}$line${C_RESET}"
    echo -e "${C_MAGENTA}│$title│${C_RESET}"
    line="╰"
    for (( i=0; i<len; i++ )); do line+="─"; done
    line+="╯"
    echo -e "${C_MAGENTA}$line${C_RESET}"
}

# Central test runner function
# Usage: run_test "Description" "command_to_run" "validation_type" "expected_value"
function run_test() {
    local description="$1"
    local command_str="$2"
    local validation_type="$3" # 'count', 'contains', 'not_contains', 'is_empty'
    local expected="$4"

    TEST_COUNT=$((TEST_COUNT + 1))
    echo -e "★ ${C_BOLD}${description}${C_RESET}"
    echo -e "→ ${C_GREY}Command: ${command_str}${C_RESET}"

    local output
    local exit_code
    
    # Safely execute command, capturing output and exit code
    output=$(eval "$command_str" 2>&1)
    exit_code=$?
    
    local success=0
    local reason=""

    case "$validation_type" in
        count)
            local result_count
            result_count=$(echo "$output" | grep -v "Searched .* directories" | grep -c .)
            if [[ -z "$result_count" ]]; then result_count=0; fi
            if [ "$result_count" -eq "$expected" ]; then
                success=1
            else
                reason="Expected count '${expected}', but got '${result_count}'."
            fi
            ;;
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
        is_empty)
            local filtered_output
            filtered_output=$(echo "$output" | grep -v "Searched .* directories")
            if [[ -z "$filtered_output" ]]; then
                success=1
            else
                reason="Expected empty output, but got content."
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

# --- Test Environment Setup ---
function setup_test_environment() {
    print_box_title "SNIPER: fastfind - Automated Test Suite"
    echo -e "${C_YELLOW}Setting up test environment in './${TEST_DIR}'...${C_RESET}"
    rm -rf "$TEST_DIR"
    mkdir -p "$TEST_DIR/subdir"
    
    # Files
    echo "hello world, this is a sample" > "$TEST_DIR/file1.txt"
    touch "$TEST_DIR/file2.log"
    echo "This is an old file" > "$TEST_DIR/old.txt"
    touch -d "40 days ago" "$TEST_DIR/old.txt" # For mtime test
    head -c 20K /dev/urandom > "$TEST_DIR/bigfile.bin"
    touch "$TEST_DIR/subdir/nested.txt"
    
    # Symlink
    ln -s ../file1.txt "$TEST_DIR/link1"
    
    # File for delete test
    touch "$TEST_DIR/temp_delete.tmp"

    echo -e "${C_YELLOW}Setup complete.${C_RESET}\n"
}

# --- Main Execution ---
function main() {
  if [ ! -x "$EXECUTABLE" ]; then
    echo -e "${C_RED}FATAL: Executable '$EXECUTABLE' not found. Please run 'make' first.${C_RESET}"
    exit 1
  fi
  
  setup_test_environment

  # --- Test Suite ---
  run_test "Basic regex match" "$EXECUTABLE -p 'file.*' -d $TEST_DIR" "count" 3
  run_test "Filter by extension (.txt)" "$EXECUTABLE -p '.*' -d $TEST_DIR -e txt" "count" 3
  run_test "Filter by type: directory" "$EXECUTABLE -p '.*' -d $TEST_DIR -t d" "count" 1
  run_test "Filter by type: symlink" "$EXECUTABLE -p '.*' -d $TEST_DIR -t l" "count" 1
  run_test "Filter by size >10K" "$EXECUTABLE -p '.*' -d $TEST_DIR --size +10K" "count" 1
  run_test "Filter by mtime <7d (newer than 7 days)" "$EXECUTABLE -p '.*' -d $TEST_DIR --mtime -7d" "count" 5
  run_test "Filter by owner (current user)" "$EXECUTABLE -p '.*' -d $TEST_DIR --owner $CURRENT_USER" "count" 7
  run_test "Filter by permissions (644)" "chmod 644 $TEST_DIR/file1.txt && $EXECUTABLE -p 'file1' -d $TEST_DIR --perms 644" "count" 1
  run_test "Content search inside files" "$EXECUTABLE -p '.*' -d $TEST_DIR --content 'hello'" "count" 1
  run_test "Content search with line number" "$EXECUTABLE -p '.*' -d $TEST_DIR --content 'sample' --with-line-number" "contains" "$TEST_DIR/file1.txt:1:"
  run_test "Ignore case search" "$EXECUTABLE -p 'BIGFILE' -d $TEST_DIR -i" "count" 1
  run_test "Exclude directory" "$EXECUTABLE -p '.*' -d $TEST_DIR --exclude subdir" "count" 5
  run_test "Max depth 1 (should find subdir but not nested.txt)" "$EXECUTABLE -p '.*' -d $TEST_DIR -m 1" "count" 6
  run_test "Long listing format" "$EXECUTABLE -p 'file1.txt' -d $TEST_DIR -l" "contains" "-rw"
  run_test "JSON output" "$EXECUTABLE -p 'file1.txt' -d $TEST_DIR --format json" "contains" '"path":"fastfind_test_dir/file1.txt"'
  run_test "CSV output" "$EXECUTABLE -p 'file1.txt' -d $TEST_DIR --format csv" "contains" '"fastfind_test_dir/file1.txt",f,'
  run_test "Write output to file" "$EXECUTABLE -p '.*' -d $TEST_DIR -o result.txt && cat result.txt" "count" 7
  run_test "Exec option" "$EXECUTABLE -p 'file.*' -d $TEST_DIR --exec 'echo Found:{}'" "contains" "Found:${TEST_DIR}/file1.txt"
  run_test "Delete option" "$EXECUTABLE -p 'temp_delete.tmp' -d $TEST_DIR --delete && $EXECUTABLE -p 'temp_delete.tmp' -d $TEST_DIR" "is_empty"

  # --- Final Report ---
  print_box_title "Final Test Report"
  for i in "${!TEST_RESULTS[@]}"; do
    echo -e " $(($i + 1)). ${TEST_RESULTS[$i]}"
  done
  echo ""
  echo -e "★ Passed: ${C_GREEN}${PASS_COUNT}${C_RESET}   ★ Failed: ${C_RED}${FAIL_COUNT}${C_RESET}   Total: ${C_BOLD}${TEST_COUNT}${C_RESET}"

  if [ $FAIL_COUNT -ne 0 ]; then
    exit 1
  fi
}

main
