#!/bin/bash

# ==============================================================================
# Robust and Modular Test Script for the 'run' Universal Code Runner
# Version: 3.0
#
# This script uses a function-based structure for clean test organization
# and a centralized result checker to eliminate code duplication.
# ==============================================================================

# --- Configuration & Globals ---
set -e # Exit immediately if a command exits with a non-zero status.
RUN_EXECUTABLE="./bin/run"
TEST_DIR=$(mktemp -d)

# --- Colors ---
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_BLUE='\033[0;34m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

# --- Counters ---
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
TOTAL_TESTS=0

# --- Trap for cleanup ---
# This ensures the temporary directory is always removed on script exit.
trap "rm -rf '$TEST_DIR'" EXIT

# --- Helper Functions ---
function print_stage() {
  echo -e "\n${C_BLUE}${C_BOLD}====== [ STAGE: $1 ] ======${C_RESET}"
}

# Central function to check test results
# Usage: check_result "Description" "$exit_code" "$output" "expected_exit_code" "expected_output_pattern"
function check_result() {
  local description="$1"
  local exit_code="$2"
  local output="$3"
  local expected_exit_code="$4"
  local expected_output="$5"
  
  TOTAL_TESTS=$((TOTAL_TESTS + 1))
  echo -en "  - Test: ${description} ..."

  if [ "$exit_code" -ne "$expected_exit_code" ]; then
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo -e " ${C_RED}[FAIL]${C_RESET}"
    echo -e "    ${C_RED}↳ Reason: Incorrect exit code. Expected ${expected_exit_code}, got ${exit_code}.${C_RESET}"
    echo -e "    ${C_RED}↳ Output was:${C_RESET}\n$output"
    return
  fi

  if ! [[ "$output" == $expected_output ]]; then
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo -e " ${C_RED}[FAIL]${C_RESET}"
    echo -e "    ${C_RED}↳ Reason: Unexpected output.${C_RESET}"
    echo -e "    ${C_RED}↳ Expected pattern: ${expected_output}${C_RESET}"
    echo -e "    ${C_RED}↳ Actual output:    ${output}${C_RESET}"
    return
  fi
  
  PASS_COUNT=$((PASS_COUNT + 1))
  echo -e " ${C_GREEN}[PASS]${C_RESET}"
}

# --- Test File Setup ---
function setup_test_files() {
  print_stage "Setting up test files in $TEST_DIR"

  # C file for compilation tests
  cat > "$TEST_DIR/hello.c" <<EOF
#include <stdio.h>
int main() { printf("Hello C"); return 0; }
EOF

  # Python file for interpreter and argument tests
  cat > "$TEST_DIR/args.py" <<EOF
import sys
print("Args:", " ".join(sys.argv[1:]))
EOF
  
  # C file for memory limit tests
  cat > "$TEST_DIR/mem_hog.c" <<EOF
#include <stdlib.h>
#include <string.h>
int main() { 
    void *p = malloc(20 * 1024 * 1024); // 20MB
    if (p) { memset(p, 0, 20 * 1024 * 1024); } // Ensure memory is allocated
    return 0; 
}
EOF

  # Shell scripts for parallel tests
  echo 'echo "Script 1"' > "$TEST_DIR/p1.sh"; chmod +x "$TEST_DIR/p1.sh"
  echo 'echo "Script 2"' > "$TEST_DIR/p2.sh"; chmod +x "$TEST_DIR/p2.sh"
}

# --- Test Suites ---
function run_basic_tests() {
  print_stage "Basic Features"
  
  local output
  local exit_code
  
  output=$($RUN_EXECUTABLE "$TEST_DIR/hello.c")
  exit_code=$?
  check_result "C compilation and execution" "$exit_code" "$output" 0 "Hello C"

  output=$($RUN_EXECUTABLE "$TEST_DIR/args.py" arg1 "hello world")
  exit_code=$?
  check_result "Python interpretation and arguments" "$exit_code" "$output" 0 "Args: arg1 hello world"
}

function run_reporting_tests() {
  print_stage "Reporting & Resource Limits"

  local output
  local exit_code

  output=$($RUN_EXECUTABLE --time "$TEST_DIR/hello.c" 2>&1)
  exit_code=$?
  check_result "Time and memory reporting" "$exit_code" "$output" 0 "*Real time*Max memory usage*"
  
  # Conditional test for memory limits
  TOTAL_TESTS=$((TOTAL_TESTS + 1))
  echo -en "  - Test: Memory limit enforcement ..."
  if [ -n "$TERMUX_VERSION" ]; then
    SKIP_COUNT=$((SKIP_COUNT + 1))
    echo -e " ${C_YELLOW}[SKIPPED]${C_RESET}"
    echo -e "    ${C_YELLOW}↳ Reason: Resource limits are not reliably enforced on Termux/Android.${C_RESET}"
  else
    output=$($RUN_EXECUTABLE --limit-mem 8192 "$TEST_DIR/mem_hog.c" 2>&1)
    exit_code=$?
    # For this test, we expect ANY non-zero exit code. The output is unpredictable.
    if [ "$exit_code" -ne 0 ]; then
        PASS_COUNT=$((PASS_COUNT + 1))
        echo -e " ${C_GREEN}[PASS]${C_RESET}"
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo -e " ${C_RED}[FAIL]${C_RESET}"
        echo -e "    ${C_RED}↳ Reason: Process was expected to be terminated but it succeeded.${C_RESET}"
    fi
  fi
}

function run_advanced_tests() {
  print_stage "Advanced Modes"

  local output
  local exit_code

  output=$($RUN_EXECUTABLE --parallel "$TEST_DIR/p1.sh" "$TEST_DIR/p2.sh" 2>&1)
  exit_code=$?
  check_result "Parallel execution" "$exit_code" "$output" 0 "*p1.sh] Finished Successfully*p2.sh] Finished Successfully*"

  output=$($RUN_EXECUTABLE --verbose "$TEST_DIR/hello.c" 2>&1)
  exit_code=$?
  check_result "Verbose mode output" "$exit_code" "$output" 0 "*Executing command:*gcc*"
}

function run_error_handling_tests() {
  print_stage "Error Handling"

  local output
  local exit_code

  touch "$TEST_DIR/file.unknown"
  output=$($RUN_EXECUTABLE "$TEST_DIR/file.unknown" 2>&1)
  exit_code=$?
  check_result "Unsupported file type" "$exit_code" "$output" 1 "*[ERROR]*Unsupported or unrecognized file type*"

  output=$($RUN_EXECUTABLE --help 2>&1)
  exit_code=$?
  check_result "Help message display" "$exit_code" "$output" 0 "*Usage:*"
}

# --- Main Execution Logic ---
function main() {
  echo -e "${C_BOLD}Starting test suite for the 'run' tool (v3.0)...${C_RESET}"

  if [ ! -x "$RUN_EXECUTABLE" ]; then
    echo -e "${C_RED}FATAL: Executable '$RUN_EXECUTABLE' not found or not executable. Please compile it first.${C_RESET}"
    exit 1
  fi

  setup_test_files
  run_basic_tests
  run_reporting_tests
  run_advanced_tests
  run_error_handling_tests

  # Final Report
  echo -e "\n${C_BLUE}${C_BOLD}====== [ TEST REPORT ] ======${C_RESET}"
  echo -e "${C_BOLD}Total defined: ${TOTAL_TESTS}${C_RESET} | ${C_GREEN}Passed: ${PASS_COUNT}${C_RESET} | ${C_RED}Failed: ${FAIL_COUNT}${C_RESET} | ${C_YELLOW}Skipped: ${SKIP_COUNT}${C_RESET}"

  if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "\n${C_GREEN}${C_BOLD}✅ All checks passed!${C_RESET}"
    exit 0
  else
    echo -e "\n${C_RED}${C_BOLD}❌ Some checks failed.${C_RESET}"
    exit 1
  fi
}

# Run the main function
main
