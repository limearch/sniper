#!/bin/bash

# Setup a test directory structure
rm -rf test_dir
mkdir -p test_dir/subdir1/subdir2
touch test_dir/file1.txt
touch test_dir/file2.log
touch test_dir/subdir1/anotherfile.TXT
touch test_dir/subdir1/subdir2/deepfile.log
echo "Hello World" > test_dir/file1.txt
echo "another line" > test_dir/subdir1/anotherfile.TXT

EXECUTABLE=./bin/fastfind
PASSED=0
FAILED=0

# Helper function for tests
assert_count() {
    local description="$1"
    local command="$2"
    local expected_count="$3"
    
    local result_count=$($command | wc -l)
    
    if [ "$result_count" -eq "$expected_count" ]; then
        echo "✅ PASS: $description"
        PASSED=$((PASSED + 1))
    else
        echo "❌ FAIL: $description (Expected $expected_count, got $result_count)"
        $command
        FAILED=$((FAILED + 1))
    fi
}

echo "--- Running Basic Functionality Tests ---"

# Test 1: Find all files by extension
assert_count "Find all .log files" "$EXECUTABLE -p '.*' -d test_dir -e log" 2

# Test 2: Find all .txt files (case-insensitive ext)
assert_count "Find all .txt files (case-insensitive)" "$EXECUTABLE -p '.*' -d test_dir -e txt -i" 2

# Test 3: Find file by specific name pattern
assert_count "Find 'file1.txt' by pattern" "$EXECUTABLE -p '^file1' -d test_dir" 1

# Test 4: Max depth 0
assert_count "Max depth 0 (current dir only)" "$EXECUTABLE -p '.*' -d test_dir -m 0" 2

# Test 5: Max depth 1
assert_count "Max depth 1" "$EXECUTABLE -p '.*' -d test_dir -m 1" 4

# Test 6: Find directories only
assert_count "Find directories only" "$EXECUTABLE -p '.*' -d test_dir -t d" 2

# Test 7: JSON output valid (check if it starts with [ and ends with ])
echo "--- Testing JSON Output ---"
JSON_OUTPUT=$($EXECUTABLE -p 'file1' -d test_dir --format json)
if [[ "$JSON_OUTPUT" == *"\"path\": \"test_dir/file1.txt\""* ]]; then
    echo "✅ PASS: JSON output contains correct path"
    PASSED=$((PASSED + 1))
else
    echo "❌ FAIL: JSON output is malformed or incorrect"
    echo "$JSON_OUTPUT"
    FAILED=$((FAILED + 1))
fi


echo "----------------------------------------"
echo "Tests Finished: $PASSED Passed, $FAILED Failed"
echo "----------------------------------------"

# Cleanup
rm -rf test_dir

if [ "$FAILED" -ne 0 ]; then
    exit 1
fi