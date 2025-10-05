#!/bin/bash

# Automated Test Script for the 'compress' tool

# --- Configuration ---
TOOL_NAME="./compress"
TEST_DIR="sample_project"
LOG_FILE="test_results.log"

# --- Colors for output ---
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_NC='\033[0m' # No Color

# --- Helper Functions ---

# Function to print a success message
print_success() {
    echo -e "${COLOR_GREEN}✔ SUCCESS: $1${COLOR_NC}"
}

# Function to print a failure message and exit
print_failure() {
    echo -e "${COLOR_RED}✘ FAILURE: $1${COLOR_NC}"
    echo "Check '$LOG_FILE' for more details."
    # Optional: exit on first failure
    # cleanup
    # exit 1
}

# Function to set up the test environment
setup() {
    echo -e "${COLOR_YELLOW}--- Setting up test environment ---${COLOR_NC}"
    cleanup > /dev/null 2>&1
    mkdir -p "$TEST_DIR/subdir"
    echo "This is the first file." > "$TEST_DIR/file1.txt"
    echo "This is a log file." > "$TEST_DIR/subdir/file2.log"
    echo "This is a hidden file." > "$TEST_DIR/.hidden_file"
    echo "main() {}" > "$TEST_DIR/program.c"
    echo "Script content" > "$TEST_DIR/script.sh"
    echo "Setup complete."
}

# Function to clean up all generated files
cleanup() {
    echo -e "${COLOR_YELLOW}--- Cleaning up ---${COLOR_NC}"
    make clean > /dev/null 2>&1
    rm -rf "$TEST_DIR"
    rm -f *.zip *.tar.gz *.tar.bz2 *.tar.xz "$LOG_FILE"
    echo "Cleanup complete."
}

# --- Main Test Execution ---

# Redirect all output to a log file and also print to stdout
exec > >(tee -a "$LOG_FILE") 2>&1

# 1. SETUP
setup

# 2. BUILD
echo -e "${COLOR_YELLOW}--- Building the tool ---${COLOR_NC}"
if ! make; then
    print_failure "Build failed. Check compilation errors above."
    exit 1
fi
print_success "Build was successful."

# 3. RUN TESTS
echo -e "${COLOR_YELLOW}--- Running functional tests ---${COLOR_NC}"

# Test 1: Basic ZIP compression
echo "Running Test 1: Basic ZIP..."
$TOOL_NAME -d $TEST_DIR -o archive.zip
if [ $? -eq 0 ] && [ -f archive.zip ]; then
    # Check content (should have 4 entries: subdir, file1.txt, subdir/file2.log, program.c, script.sh, but not .hidden_file initially)
    # Note: zip_folder was improved to handle hidden files, so let's test for its presence.
    unzip -l archive.zip | grep -q "file1.txt" && unzip -l archive.zip | grep -q ".hidden_file"
    if [ $? -eq 0 ]; then
        print_success "Basic ZIP compression works."
    else
        print_failure "Basic ZIP archive content is incorrect."
    fi
else
    print_failure "Basic ZIP compression failed."
fi

# Test 2: Skip Hidden Files (ZIP)
echo "Running Test 2: Skip Hidden Files..."
$TOOL_NAME -d $TEST_DIR -o nohidden.zip -H
if [ $? -eq 0 ] && [ -f nohidden.zip ]; then
    # Content should NOT contain .hidden_file
    ! unzip -l nohidden.zip | grep -q ".hidden_file"
    if [ $? -eq 0 ]; then
        print_success "Skip hidden files option (-H) works."
    else
        print_failure "Skip hidden files option (-H) failed; hidden file was found."
    fi
else
    print_failure "Skip hidden files command failed."
fi

# Test 3: Filter Extension (ZIP)
echo "Running Test 3: Filter by extension (.c)..."
$TOOL_NAME -d $TEST_DIR -o c_only.zip -f .c
if [ $? -eq 0 ] && [ -f c_only.zip ]; then
    # Should only contain program.c (and parent dirs)
    unzip -l c_only.zip | grep -q "program.c" && ! unzip -l c_only.zip | grep -q "file1.txt"
    if [ $? -eq 0 ]; then
        print_success "Filter files option (-f .c) works."
    else
        print_failure "Filter files option (-f .c) content is incorrect."
    fi
else
    print_failure "Filter files command failed."
fi

# Test 4: Exclude Extension (ZIP)
echo "Running Test 4: Exclude extension (.sh)..."
$TOOL_NAME -d $TEST_DIR -o no_sh.zip -e .sh
if [ $? -eq 0 ] && [ -f no_sh.zip ]; then
    # Should NOT contain script.sh
    ! unzip -l no_sh.zip | grep -q "script.sh" && unzip -l no_sh.zip | grep -q "file1.txt"
    if [ $? -eq 0 ]; then
        print_success "Exclude files option (-e .sh) works."
    else
        print_failure "Exclude files option (-e .sh) content is incorrect."
    fi
else
    print_failure "Exclude files command failed."
fi

# Test 5: TAR Gzip Compression
echo "Running Test 5: TAR Gzip..."
$TOOL_NAME -d $TEST_DIR -o archive.tar.gz -C gzip
if [ $? -eq 0 ] && [ -f archive.tar.gz ]; then
    print_success "TAR Gzip compression works."
else
    print_failure "TAR Gzip compression failed."
fi

# Test 6: TAR Bzip2 Compression
echo "Running Test 6: TAR Bzip2..."
$TOOL_NAME -d $TEST_DIR -o archive.tar.bz2 -C bzip2
if [ $? -eq 0 ] && [ -f archive.tar.bz2 ]; then
    print_success "TAR Bzip2 compression works."
else
    print_failure "TAR Bzip2 compression failed."
fi

# Test 7: Error Handling (Missing Arguments)
echo "Running Test 7: Error handling for missing arguments..."
$TOOL_NAME -d $TEST_DIR > /dev/null 2>&1 # Redirect output to hide expected error message
if [ $? -ne 0 ]; then
    print_success "Error handling for missing output file works."
else
    print_failure "Error handling for missing output file failed (expected non-zero exit code)."
fi

# 4. CLEANUP
cleanup

echo -e "${COLOR_GREEN}--- All tests completed ---${COLOR_NC}"