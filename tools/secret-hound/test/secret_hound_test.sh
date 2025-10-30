#!/bin/bash

# ==============================================================================
# SNIPER: secret-hound - Automated Test Suite
# ==============================================================================

# --- Configuration & Globals ---
EXECUTABLE="../tools/secret-hound/bin/secret-hound"
TEST_DIR="hound_test_dir"

# --- Colors for Output ---
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_RESET='\033[0m'
C_BOLD='\033[1m'

# --- State Management ---
PASS_COUNT=0
FAIL_COUNT=0

# --- Cleanup Trap ---
trap "echo -e '\n${C_YELLOW}Cleaning up test environment...${C_RESET}'; rm -rf '$TEST_DIR'" EXIT

# --- Helper Functions ---
function run_test() {
    local description="$1"
    local command_str="$2"
    local expected_to_contain="$3"

    echo -e "🧪 Running Test: ${C_BOLD}${description}${C_RESET}"
    
    # We need to pipe the output to the Python reporter for a full test
    local reporter_path="../tools/secret-hound/ui/reporter.py"
    local full_command="$command_str | python3 $reporter_path"

    local output
    output=$(eval "$full_command" 2>&1)
    
    if echo "$output" | grep -q -- "$expected_to_contain"; then
        echo -e "  ${C_GREEN}[✔] PASS${C_RESET}"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "  ${C_RED}[✘] FAIL${C_RESET}: Expected output to contain '${expected_to_contain}'"
        echo -e "--- OUTPUT ---"
        echo "$output"
        echo "--------------"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    echo ""
}

# --- Test Environment Setup ---
function setup_test_environment() {
    echo -e "${C_YELLOW}Setting up test environment in './${TEST_DIR}'...${C_RESET}"
    rm -rf "$TEST_DIR"
    mkdir -p "$TEST_DIR/config"
    mkdir -p "$TEST_DIR/src"
    
    # File with a clear secret
    echo "const AWS_KEY = 'AKIAIOSFODNN7EXAMPLE';" > "$TEST_DIR/config/keys.js"
    # File with a high-entropy string
    echo "SESSION_SECRET=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4" > "$TEST_DIR/config/session.env"
    # A normal file
    echo "console.log('Hello World');" > "$TEST_DIR/src/index.js"

    echo -e "${C_YELLOW}Setup complete.${C_RESET}\n"
}

# --- Main Execution ---
function main() {
  if [ ! -x "$EXECUTABLE" ]; then
    echo -e "${C_RED}FATAL: Executable '$EXECUTABLE' not found. Please build the project first.${C_RESET}"
    exit 1
  fi
  
  setup_test_environment

  run_test "Find AWS Key" "$EXECUTABLE $TEST_DIR" "AWS_ACCESS_KEY"
  run_test "Find high entropy generic secret" "$EXECUTABLE $TEST_DIR" "GENERIC_HIGH_ENTROPY"
  run_test "Check total findings count" "$EXECUTABLE $TEST_DIR" "Found 2 potential secret(s)"

  echo "----------------------------------------"
  echo "Tests Finished: ${C_GREEN}${PASS_COUNT} Passed${C_RESET}, ${C_RED}${FAIL_COUNT} Failed${C_RESET}"
  echo "----------------------------------------"

  if [ $FAIL_COUNT -ne 0 ]; then
    exit 1
  fi
}

main
